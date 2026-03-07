import asyncio
import json
import os
import secrets as _secrets
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from urllib.parse import urlencode
from uuid import UUID

import httpx
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.responses import JSONResponse, StreamingResponse, RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert
import uvicorn
from mcp.server.sse import SseServerTransport
from mcp.server import Server
from mcp.server.models import InitializationOptions
from starlette.responses import Response

from .database import get_db, engine, get_db_session
from .models import MCPClient, WordPressSite
from .schemas import MCPClientCreate, MCPClientResponse
from .aicms_mcp_server.server import MCPServer

# FastAPI app
app = FastAPI(
    title="AI CMS MCP Server",
    description="Hosted MCP server for AI CMS integration",
    version="1.0.0"
)

# Security
security = HTTPBearer(auto_error=False)

# MCP server instance
mcp_server = None

# Per-client SSE queues: client_id → asyncio.Queue of JSON-RPC response dicts
_sse_queues: dict[str, asyncio.Queue] = {}

# RFC 7591 dynamically registered OAuth clients: client_id → client_secret
_registered_oauth_clients: dict[str, str] = {}


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> str:
    """Get user ID from request header"""
    # Check for user ID in X-User-ID header (from backend proxy)
    user_id = request.headers.get("X-User-ID")
    if user_id:
        return user_id
    
    # Fallback to Bearer token for direct MCP client access
    credentials = await security(request)
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authentication provided"
        )
    
    # Find MCP client by token
    result = await db.execute(
        select(MCPClient)
        .where(MCPClient.token == credentials.credentials)
        .where(MCPClient.expires_at > datetime.utcnow())
    )
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return str(client.user_id)


async def _call_wp_tool(wp_mcp_token: str, tool: str, args: dict) -> str:
    """Proxy a WP tool call to the backend dispatch endpoint.

    Returns a human-readable string for the MCP content block.
    """
    api_url = os.getenv("API_URL", "http://backend:8000/api")
    internal_secret = os.getenv("INTERNAL_SECRET", "")
    url = f"{api_url}/wordpress/wp-mcp/{wp_mcp_token}/dispatch"
    headers = {"X-Internal-Secret": internal_secret, "Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json={"tool": tool, "args": args}, headers=headers)
    except Exception as exc:
        return f"Error contacting backend: {exc}"

    if response.status_code == 404:
        return (
            "WordPress site not found for this token. "
            "Register your WP site at mystorey.io/dashboard/wordpress."
        )
    if response.status_code == 403:
        return "Internal authentication error. Contact support."
    if not response.is_success:
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        return f"WordPress error: {detail}"

    data = response.json()
    result = data.get("result", data)

    # Format result as readable text
    if isinstance(result, list):
        import json as _json
        return _json.dumps(result, indent=2, default=str)
    if isinstance(result, dict):
        # For create/update operations, produce a compact summary
        title = result.get("title", {})
        if isinstance(title, dict):
            title = title.get("rendered", title.get("raw", ""))
        rid = result.get("id")
        rstatus = result.get("status")
        rlink = result.get("link", "")
        if rid and rstatus:
            return f"Post/Page '{title}' (id={rid}) — status: {rstatus}. URL: {rlink}"
        import json as _json
        return _json.dumps(result, indent=2, default=str)
    return str(result)


@app.on_event("startup")
async def startup_event():
    """Initialize MCP server and create tables"""
    global mcp_server
    
    # Create tables
    from .database import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    api_url = os.getenv("API_URL", "http://localhost:8000/api")
    mcp_server = MCPServer(api_url, None, os.getenv("APP_URL", ""))  # Token not needed for hosted version


@app.get("/")
async def root():
    """Root endpoint"""
    return {"service": "AI CMS MCP Server", "version": "1.0.0", "status": "running"}


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy"}


@app.get("/.well-known/oauth-authorization-server")
async def oauth_server_info(request: Request):
    """OAuth server discovery endpoint"""
    # Use forwarded headers to get the public scheme/host (ngrok, proxies)
    scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
    host = request.headers.get("host", "localhost:8000")
    base_url = f"{scheme}://{host}"
    
    return {
        "issuer": base_url,
        "authorization_endpoint": f"{base_url}/authorize",
        "token_endpoint": f"{base_url}/token",
        "registration_endpoint": f"{base_url}/oauth/register",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "scopes_supported": ["mcp", "openid", "profile", "offline_access"],
        "code_challenge_methods_supported": ["S256", "plain"],
        "token_endpoint_auth_methods_supported": ["none", "client_secret_post", "client_secret_basic"],
    }


@app.get("/mcp/.well-known/oauth-protected-resource")
async def mcp_scoped_protected_resource(request: Request):
    """Some clients (e.g. Perplexity) look for resource metadata scoped to /mcp/."""
    return await oauth_protected_resource(request)


@app.get("/.well-known/oauth-protected-resource")
async def oauth_protected_resource(request: Request):
    """OAuth protected resource endpoint"""
    scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
    host = request.headers.get("host", "localhost:8000")
    base_url = f"{scheme}://{host}"

    return {
        "resource": base_url,
        "authorization_servers": [base_url],
        "scopes_supported": ["mcp"],
    }


@app.get("/.well-known/oauth-protected-resource/mcp-sse/sse/{client_id}")
async def oauth_protected_resource_sse(client_id: str):
    """OAuth protected resource for SSE endpoint"""
    return {"endpoint": f"/mcp-sse/sse/{client_id}"}


@app.get("/.well-known/oauth-protected-resource/mcp/{client_id}")
async def oauth_protected_resource_mcp(client_id: str):
    """OAuth protected resource for MCP endpoint"""
    return {"endpoint": f"/mcp/{client_id}"}


@app.get("/authorize")
async def authorize(
    response_type: str = "code",
    client_id: str = None,
    redirect_uri: str = None,
    code_challenge: str = None,
    code_challenge_method: str = None,
    state: str = None,
    scope: str = None,
    request: Request = None,
):
    """OAuth authorization endpoint — redirect to the frontend consent page."""
    print(f"[authorize] client_id={client_id} redirect_uri={redirect_uri} state={state} code_challenge={'present' if code_challenge else 'absent'}")
    scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
    host = request.headers.get("host", "localhost")
    frontend_url = f"{scheme}://{host}"
    # Build params dict and URL-encode properly so redirect_uri with ://?& is not misinterpreted
    params: dict = {}
    if redirect_uri:
        params["redirect_uri"] = redirect_uri
    if state:
        params["state"] = state
    if code_challenge:
        params["code_challenge"] = code_challenge
    if code_challenge_method:
        params["code_challenge_method"] = code_challenge_method
    if client_id:
        params["client_id"] = client_id
    qs = urlencode(params)
    url = f"{frontend_url}/connect?{qs}"
    print(f"[authorize] redirecting to {url}")
    return RedirectResponse(url=url, status_code=302)


@app.post("/token")
async def token(request: Request):
    """OAuth token endpoint - returns access token for Claude Desktop"""
    # Claude Desktop uses client credentials flow
    try:
        content_type = request.headers.get("content-type", "")
        
        if "application/json" in content_type:
            body = await request.body()
            data = json.loads(body.decode())
        elif "application/x-www-form-urlencoded" in content_type:
            form = await request.form()
            data = dict(form)
        else:
            # Try JSON first, then form
            body = await request.body()
            if body:
                try:
                    data = json.loads(body.decode())
                except:
                    form = await request.form()
                    data = dict(form)
            else:
                form = await request.form()
                data = dict(form)
    except Exception as e:
        data = {}
    
    code = data.get("code", "")
    client_secret = data.get("client_secret", "")
    grant_type = data.get("grant_type", "")
    client_id_param = data.get("client_id", "")
    redirect_uri_param = data.get("redirect_uri", "")
    code_verifier = data.get("code_verifier", "")
    print(f"[token] grant_type={grant_type} code={'present' if code else 'absent'} client_id={client_id_param} redirect_uri={redirect_uri_param} client_secret={'present' if client_secret else 'absent'} code_verifier={'present' if code_verifier else 'absent'}")

    # Authorization code flow: exchange code via backend
    if code:
        api_url = os.getenv("API_URL", "http://backend:8000/api")
        exchange_params: dict = {"code": code}
        if code_verifier:
            exchange_params["code_verifier"] = code_verifier
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{api_url}/mcp/exchange-code", params=exchange_params)
            print(f"[token] exchange-code response: status={resp.status_code} body={resp.text[:200]}")
            if resp.status_code == 200:
                mcp_token = resp.json()["token"]
                print(f"[token] success — issued access_token (truncated): {mcp_token[:8]}...")
                return {
                    "access_token": mcp_token,
                    "token_type": "Bearer",
                    "expires_in": 86400,
                }
        print(f"[token] code exchange FAILED — returning 401")

    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/register", response_model=MCPClientResponse)
async def register_mcp_client(
    client_data: MCPClientCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new MCP client for AI tools"""
    
    # Generate unique token
    import secrets
    token = secrets.token_urlsafe(32)
    
    # Create client
    expires_at = datetime.utcnow() + timedelta(days=365)  # 1 year expiry
    
    db_client = MCPClient(
        name=client_data.name,
        user_id=client_data.user_id,
        tool_type=client_data.tool_type,  # claude, chatgpt, cursor
        token=token,
        expires_at=expires_at,
        extra_data=client_data.extra_data or {}
    )
    
    db.add(db_client)
    await db.commit()
    await db.refresh(db_client)
    
    return MCPClientResponse(
        id=db_client.id,
        name=db_client.name,
        tool_type=db_client.tool_type,
        token=token,
        expires_at=expires_at,
        created_at=db_client.created_at
    )


@app.post("/oauth/register")
async def register_oauth_client(request: Request):
    """RFC 7591 Dynamic Client Registration — called by Claude.ai before starting OAuth."""
    body: dict = {}
    try:
        body = await request.json()
    except Exception:
        pass

    client_id = str(uuid.uuid4())
    client_secret = _secrets.token_urlsafe(32)
    # Echo back redirect_uris from the request (RFC 7591 requirement)
    redirect_uris = body.get("redirect_uris", ["https://claude.ai/api/mcp/auth_callback"])
    _registered_oauth_clients[client_id] = {"secret": client_secret, "redirect_uris": redirect_uris}
    print(f"[DCR] Registered OAuth client: {client_id}, redirect_uris={redirect_uris}, request_body_keys={list(body.keys())}")
    return JSONResponse(
        status_code=201,
        content={
            "client_id": client_id,
            "client_secret": client_secret,
            "client_id_issued_at": int(datetime.utcnow().timestamp()),
            "client_secret_expires_at": 0,
            "redirect_uris": redirect_uris,
            "grant_types": ["authorization_code"],
            "response_types": ["code"],
            "token_endpoint_auth_method": "client_secret_post",
            "scope": "mcp",
        },
    )


@app.post("/mcp")
async def mcp_generic_endpoint(
    body: Dict[str, Any],
    http_req: Request,
    db: AsyncSession = Depends(get_db),
):
    """Generic MCP Streamable HTTP endpoint — URL has no user identifier.
    The Bearer token (= MCP token) identifies the user.
    This is the preferred URL to share with Claude.ai / Claude Desktop.
    """
    scheme = http_req.headers.get("x-forwarded-proto", http_req.url.scheme)
    host = http_req.headers.get("host", "localhost")
    resource_metadata = f"{scheme}://{host}/.well-known/oauth-protected-resource"

    auth_header = http_req.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"error": "unauthorized", "error_description": "Bearer token required"},
            headers={"WWW-Authenticate": f'Bearer resource_metadata="{resource_metadata}"'},
        )

    token = auth_header[7:]
    result = await db.execute(
        select(MCPClient)
        .where(MCPClient.token == token)
        .where(MCPClient.expires_at > datetime.utcnow())
    )
    authed_client = result.scalar_one_or_none()

    # Check if this is a WordPress mcp_token (WP users paste their mcp_token directly)
    wp_token: str | None = None
    wp_site: WordPressSite | None = None
    if not authed_client:
        wp_row = await db.execute(
            select(WordPressSite)
            .where(WordPressSite.mcp_token == token)
            .where(WordPressSite.is_active.is_(True))
        )
        wp_site = wp_row.scalar_one_or_none()
        if wp_site:
            wp_token = token
        else:
            return JSONResponse(
                status_code=401,
                content={"error": "invalid_token"},
                headers={"WWW-Authenticate": f'Bearer error="invalid_token", resource_metadata="{resource_metadata}"'},
            )

    method = body.get("method", "")
    req_id = body.get("id")
    user_id_log = wp_site.user_id if wp_token else authed_client.user_id  # type: ignore[union-attr]
    print(f"[/mcp] method={method} user={user_id_log} wp={wp_token is not None}")

    def ok(result):
        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    WP_TOOLS = {
        "wp_list_posts", "wp_create_post", "wp_update_post", "wp_publish_post",
        "wp_list_pages", "wp_create_page", "wp_update_page", "wp_publish_page",
        "wp_get_site_info", "wp_update_site_settings",
        "wp_list_categories", "wp_list_tags",
    }

    api_url = os.getenv("API_URL", "http://backend:8000/api")
    mcp_token_for_server = token if not wp_token else ""
    per_request_server = MCPServer(api_url, mcp_token_for_server, os.getenv("APP_URL", ""))

    if method == "initialize":
        return ok({
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {"listChanged": True}},
            "serverInfo": {"name": "aicms-mcp-server", "version": "1.0.0"},
        })
    elif method == "notifications/initialized":
        # Push tools/list_changed so clients that do lazy discovery (e.g. Perplexity)
        # know to call tools/list immediately after initialization.
        if authed_client:
            sse_queue = _sse_queues.get(str(authed_client.id))
            if sse_queue:
                await sse_queue.put({"jsonrpc": "2.0", "method": "notifications/tools/list_changed"})
        return {}
    elif method == "tools/list":
        return ok({"tools": _make_tool_list()})
    elif method == "tools/call":
        params = body.get("params", {})
        tool_name = params.get("name", "")
        tool_args = params.get("arguments", {})

        if tool_name in WP_TOOLS:
            # Resolve the WP site mcp_token:
            # - Direct WP token auth: wp_token is already the site's mcp_token
            # - OAuth (ChatGPT/Claude) auth: look up the user's active WP site
            if wp_token:
                effective_wp_token = wp_token
            else:
                wp_row = await db.execute(
                    select(WordPressSite)
                    .where(WordPressSite.user_id == authed_client.user_id)  # type: ignore[union-attr]
                    .where(WordPressSite.is_active.is_(True))
                    .limit(1)
                )
                user_wp_site = wp_row.scalar_one_or_none()
                if not user_wp_site:
                    return ok({"content": [{"type": "text", "text": "No WordPress site connected to your MyStorey account. Visit the dashboard to add one."}], "isError": True})
                effective_wp_token = str(user_wp_site.mcp_token)
            wp_call_result = await _call_wp_tool(effective_wp_token, tool_name, tool_args)
            return ok({"content": [{"type": "text", "text": wp_call_result}], "isError": False})

        result = await per_request_server._dispatch(tool_name, tool_args)
        return ok({"content": [{"type": c.type, "text": c.text} for c in result.content], "isError": result.isError})
    elif method == "ping":
        return ok({})
    else:
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}


@app.get("/mcp")
async def mcp_generic_sse(
    http_req: Request,
    db: AsyncSession = Depends(get_db),
):
    """GET /mcp — SSE stream for server-to-client messages (MCP Streamable HTTP spec).
    Required by Perplexity, ChatGPT, and any compliant MCP client.
    """
    scheme = http_req.headers.get("x-forwarded-proto", http_req.url.scheme)
    host = http_req.headers.get("host", "localhost")
    resource_metadata = f"{scheme}://{host}/.well-known/oauth-protected-resource"

    auth_header = http_req.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"error": "unauthorized"},
            headers={"WWW-Authenticate": f'Bearer resource_metadata="{resource_metadata}"'},
        )

    token = auth_header[7:]
    result = await db.execute(
        select(MCPClient)
        .where(MCPClient.token == token)
        .where(MCPClient.expires_at > datetime.utcnow())
    )
    authed_client = result.scalar_one_or_none()
    if not authed_client:
        return JSONResponse(
            status_code=401,
            content={"error": "invalid_token"},
            headers={"WWW-Authenticate": f'Bearer error="invalid_token", resource_metadata="{resource_metadata}"'},
        )

    client_key = str(authed_client.id)
    queue: asyncio.Queue = asyncio.Queue()
    _sse_queues[client_key] = queue

    async def event_stream():
        try:
            while True:
                if await http_req.is_disconnected():
                    break
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"event: message\ndata: {json.dumps(msg)}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            _sse_queues.pop(client_key, None)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/mcp/{client_id}")
async def mcp_endpoint(
    client_id: str,
    body: Dict[str, Any],
    http_req: Request,
    db: AsyncSession = Depends(get_db),
):
    """MCP Streamable HTTP endpoint — requires OAuth Bearer token."""
    scheme = http_req.headers.get("x-forwarded-proto", http_req.url.scheme)
    host = http_req.headers.get("host", "localhost")
    resource_metadata = f"{scheme}://{host}/.well-known/oauth-protected-resource"

    # Extract and validate Bearer token
    auth_header = http_req.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"error": "unauthorized", "error_description": "Bearer token required"},
            headers={"WWW-Authenticate": f'Bearer resource_metadata="{resource_metadata}"'},
        )

    token = auth_header[7:]
    result = await db.execute(
        select(MCPClient)
        .where(MCPClient.token == token)
        .where(MCPClient.expires_at > datetime.utcnow())
    )
    authed_client = result.scalar_one_or_none()
    if not authed_client:
        return JSONResponse(
            status_code=401,
            content={"error": "invalid_token"},
            headers={"WWW-Authenticate": f'Bearer error="invalid_token", resource_metadata="{resource_metadata}"'},
        )

    # Verify the URL client_id belongs to the same user as the token
    try:
        url_client = await db.get(MCPClient, UUID(client_id))
    except ValueError:
        return JSONResponse(status_code=404, content={"error": "not_found"})

    if not url_client or url_client.user_id != authed_client.user_id:
        return JSONResponse(status_code=403, content={"error": "forbidden"})

    api_url = os.getenv("API_URL", "http://backend:8000/api")
    per_request_server = MCPServer(api_url, url_client.token, os.getenv("APP_URL", ""))

    method = body.get("method", "")
    req_id = body.get("id")

    def ok(result):
        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    if method == "initialize":
        return ok({
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {"listChanged": True}},
            "serverInfo": {"name": "aicms-mcp-server", "version": "1.0.0"},
        })
    elif method == "notifications/initialized":
        return {}
    elif method == "tools/list":
        return ok({"tools": _make_tool_list()})
    elif method == "tools/call":
        params = body.get("params", {})
        result = await per_request_server._dispatch(params.get("name", ""), params.get("arguments", {}))
        return ok({"content": [{"type": c.type, "text": c.text} for c in result.content], "isError": result.isError})
    elif method == "ping":
        return ok({})
    else:
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}


@app.get("/clients", response_model=List[MCPClientResponse])
async def list_clients(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's MCP clients"""
    
    result = await db.execute(
        select(MCPClient)
        .where(MCPClient.user_id == UUID(user_id))
        .order_by(MCPClient.created_at.desc())
    )
    clients = result.scalars().all()
    
    return [
        MCPClientResponse(
            id=client.id,
            name=client.name,
            tool_type=client.tool_type,
            token=client.token,
            expires_at=client.expires_at,
            created_at=client.created_at
        )
        for client in clients
    ]


@app.delete("/clients/{client_id}")
async def delete_client(
    client_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an MCP client"""
    
    client = await db.get(MCPClient, client_id)
    if not client or client.user_id != UUID(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    await db.delete(client)
    await db.commit()
    
    return {"message": "Client deleted successfully"}


# SSE endpoint for Claude Desktop - supports GET (SSE), POST (Streamable HTTP), and DELETE
@app.api_route("/sse/{client_id}", methods=["GET", "POST", "DELETE"])
async def sse_endpoint(client_id: str, request: Request):
    """SSE endpoint for Claude Desktop MCP connections - supports SSE and Streamable HTTP"""
    
    print(f"MCP connection requested for client: {client_id}, method: {request.method}")
    
    # Handle DELETE request - Claude uses this to close connections
    if request.method == "DELETE":
        print(f"DELETE request for client {client_id} - acknowledging")
        return {"status": "ok"}
    
    # Check for Authorization header
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        print(f"Received token: {token}")
    else:
        print("No authorization header found")
    
    # Verify client exists
    async with get_db_session() as db:
        result = await db.execute(select(MCPClient).where(MCPClient.id == client_id))
        client = result.scalar_one_or_none()
        if not client:
            print(f"Client {client_id} not found")
            raise HTTPException(status_code=404, detail="Client not found")
    
    print(f"Client {client_id} verified")
    
    # For POST requests (Streamable HTTP), check if client wants SSE upgrade
    if request.method == "POST":
        accept_header = request.headers.get("accept", "")
        print(f"POST request with Accept: {accept_header}")
        
        # If client ONLY wants SSE stream (no JSON), return streaming response
        # Otherwise return JSON initialization (preferred when both acceptable)
        if "text/event-stream" in accept_header and "application/json" not in accept_header:
            print("Client requesting SSE stream via POST - Streamable HTTP mode")
        else:
            # Return JSON response - check if it's an MCP message first
            print("POST with JSON accepted - checking for MCP message")
            body = await request.body()
            if body:
                print(f"Received POST body: {body}")
                try:
                    message = json.loads(body.decode())
                    print(f"Parsed message: {message}")
                    
                    # Handle actual MCP messages
                    if message.get("method") == "tools/list":
                        return JSONResponse(content={"jsonrpc": "2.0", "id": message.get("id"), "result": {"tools": _make_tool_list()}})

                    elif message.get("method") == "initialize":
                        return JSONResponse(content={
                            "jsonrpc": "2.0",
                            "id": message.get("id"),
                            "result": {
                                "protocolVersion": "2024-11-05",
                                "capabilities": {"tools": {"listChanged": True}},
                                "serverInfo": {"name": "aicms-mcp-server", "version": "1.0.0"}
                            }
                        })

                    elif message.get("method") == "tools/call":
                        params = message.get("params", {})
                        try:
                            server = await _get_mcp_server_for_client(client_id)
                            result = await server._dispatch(params.get("name", ""), params.get("arguments", {}))
                            return JSONResponse(content={
                                "jsonrpc": "2.0",
                                "id": message.get("id"),
                                "result": {
                                    "content": [{"type": c.type, "text": c.text} for c in result.content],
                                    "isError": result.isError,
                                }
                            })
                        except Exception as e:
                            print(f"Error executing tool: {e}")
                            return JSONResponse(content={
                                "jsonrpc": "2.0",
                                "id": message.get("id"),
                                "result": {
                                    "content": [{"type": "text", "text": f"Error: {str(e)}"}]
                                }
                            })
                except json.JSONDecodeError:
                    pass
            
            # Default initialization response
            session_id = str(uuid.uuid4())
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {"listChanged": True}},
                        "serverInfo": {"name": "aicms-mcp-server", "version": "1.0.0"}
                    }
                },
                headers={"Mcp-Session-Id": session_id}
            )
    
    print(f"Establishing SSE connection for {client_id}")

    # Create a per-client queue for pushing responses back via SSE
    queue: asyncio.Queue = asyncio.Queue()
    _sse_queues[client_id] = queue

    async def event_stream():
        """SSE event stream for MCP protocol"""
        print("Starting SSE event stream")
        print(f"All headers: {dict(request.headers)}")

        scheme = request.headers.get('x-forwarded-proto', request.url.scheme)
        host = request.headers.get('host', 'localhost:8000')
        base_url = f"{scheme}://{host}"
        message_endpoint = f"{base_url}/sse/{client_id}/messages"

        print(f"Scheme from header: {scheme}, URL scheme: {request.url.scheme}")
        print(f"Sending endpoint event: {message_endpoint}")

        # Tell the client where to POST messages
        yield f"event: endpoint\ndata: {message_endpoint}\n\n"

        # Relay responses from the queue back to the client as SSE message events
        try:
            while True:
                if await request.is_disconnected():
                    print("Client disconnected")
                    break
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"event: message\ndata: {json.dumps(msg)}\n\n"
                except asyncio.TimeoutError:
                    # Keep-alive ping
                    yield ": keepalive\n\n"
        except asyncio.CancelledError:
            print("SSE connection cancelled")
        except Exception as e:
            print(f"SSE connection error: {e}")
        finally:
            print("Cleaning up SSE connection")
            _sse_queues.pop(client_id, None)
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


# Alternative endpoint for compatibility
@app.get("/mcp/{client_id}")
async def sse_endpoint_alt(client_id: str, request: Request):
    """Alternative SSE endpoint path for compatibility"""
    return await sse_endpoint(client_id, request)


# Alternative SSE endpoint path that Claude might expect
@app.get("/mcp-sse/sse/{client_id}")
async def sse_endpoint_alt(client_id: str, request: Request):
    """Alternative SSE endpoint path for Claude Desktop"""
    return await sse_endpoint(client_id, request)


# Message endpoint for MCP protocol
def _make_tool_list() -> list[dict]:
    """Delegate to server.py — single source of truth for all tool definitions."""
    from .aicms_mcp_server.server import get_tool_dicts
    return get_tool_dicts()


async def _get_mcp_server_for_client(client_id: str) -> MCPServer:
    """Look up MCP client by ID and return an MCPServer configured with its token."""
    api_url = os.getenv("API_URL", "http://backend:8000/api")
    async with get_db_session() as db:
        result = await db.execute(select(MCPClient).where(MCPClient.id == client_id))
        client = result.scalar_one_or_none()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        return MCPServer(api_url, client.token, os.getenv("APP_URL", ""))


@app.post("/sse/{client_id}/messages")
async def mcp_messages(client_id: str, request: Request):
    """Handle MCP protocol messages — process and push response via SSE stream."""
    body = await request.body()
    print(f"Received message for {client_id}: {body}")

    try:
        message = json.loads(body.decode())
        print(f"Parsed message: {message}")
    except Exception as e:
        print(f"Error parsing message: {e}")
        return Response(status_code=400)

    method = message.get("method", "")
    req_id = message.get("id")

    response = None
    try:
        if method == "initialize":
            response = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {"listChanged": True}},
                    "serverInfo": {"name": "aicms-mcp-server", "version": "1.0.0"},
                },
            }
        elif method == "notifications/initialized":
            pass  # No response needed
        elif method == "ping":
            response = {"jsonrpc": "2.0", "id": req_id, "result": {}}
        elif method == "tools/list":
            response = {"jsonrpc": "2.0", "id": req_id, "result": {"tools": _make_tool_list()}}
        elif method == "tools/call":
            params = message.get("params", {})
            server = await _get_mcp_server_for_client(client_id)
            result = await server._dispatch(params.get("name", ""), params.get("arguments", {}))
            response = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": c.type, "text": c.text} for c in result.content],
                    "isError": result.isError,
                },
            }
        else:
            response = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}
    except Exception as e:
        print(f"Error handling method {method}: {e}")
        response = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32000, "message": str(e)}}

    # Push response via SSE queue (MCP SSE transport requires this)
    if response is not None:
        queue = _sse_queues.get(client_id)
        if queue:
            await queue.put(response)
            print(f"Pushed response via SSE queue for {client_id}: method={method}")
        else:
            print(f"No SSE queue for {client_id} — client may have disconnected")

    # 202 Accepted is the correct SSE transport response (response goes via SSE stream)
    return Response(status_code=202)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
