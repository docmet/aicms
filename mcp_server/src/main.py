import asyncio
import json
import os
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
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
from .models import MCPClient
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


@app.on_event("startup")
async def startup_event():
    """Initialize MCP server and create tables"""
    global mcp_server
    
    # Create tables
    from .database import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    api_url = os.getenv("API_URL", "http://localhost:8000/api")
    mcp_server = MCPServer(api_url, None)  # Token not needed for hosted version


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
        "scopes_supported": ["mcp"],
        "code_challenge_methods_supported": ["S256", "plain"],
        "token_endpoint_auth_methods_supported": ["none", "client_secret_post", "client_secret_basic"],
    }


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
    print(f"[authorize] client_id={client_id} redirect_uri={redirect_uri} state={state} code_challenge={code_challenge}")
    scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
    host = request.headers.get("host", "localhost")
    frontend_url = f"{scheme}://{host}"
    params = []
    if redirect_uri:
        params.append(f"redirect_uri={redirect_uri}")
    if state:
        params.append(f"state={state}")
    if code_challenge:
        params.append(f"code_challenge={code_challenge}")
    if code_challenge_method:
        params.append(f"code_challenge_method={code_challenge_method}")
    qs = "&".join(params)
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
    print(f"[token] grant_type={grant_type} code={'present' if code else 'absent'} client_secret={'present' if client_secret else 'absent'}")

    # Authorization code flow: exchange code via backend
    if code:
        api_url = os.getenv("API_URL", "http://backend:8000/api")
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{api_url}/mcp/exchange-code", params={"code": code})
            if resp.status_code == 200:
                return {
                    "access_token": resp.json()["token"],
                    "token_type": "Bearer",
                    "expires_in": 86400,
                }

    # Fallback: client_secret = MCP token (for manual Advanced settings setup)
    if client_secret:
        async with get_db_session() as db:
            result = await db.execute(
                select(MCPClient).where(MCPClient.token == client_secret)
            )
            mcp_client = result.scalar_one_or_none()
            if mcp_client:
                return {
                    "access_token": client_secret,
                    "token_type": "Bearer",
                    "expires_in": 86400,
                }

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
    import secrets as _secrets
    client_id = str(uuid.uuid4())
    client_secret = _secrets.token_urlsafe(32)
    _registered_oauth_clients[client_id] = client_secret
    print(f"[DCR] Registered OAuth client: {client_id}")
    return JSONResponse(
        status_code=201,
        content={
            "client_id": client_id,
            "client_secret": client_secret,
            "client_id_issued_at": int(datetime.utcnow().timestamp()),
            "client_secret_expires_at": 0,
            "grant_types": ["authorization_code"],
            "response_types": ["code"],
            "token_endpoint_auth_method": "client_secret_post",
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
    per_request_server = MCPServer(api_url, url_client.token)

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
                        tools = [
                            {"name": "list_sites", "description": "List all sites", "inputSchema": {"type": "object", "properties": {}}},
                            {"name": "create_site", "description": "Create a new site", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "slug": {"type": "string"}, "theme_slug": {"type": "string"}}, "required": ["name", "slug"]}},
                            {"name": "get_site_info", "description": "Get site details", "inputSchema": {"type": "object", "properties": {"site_id": {"type": "string"}}, "required": ["site_id"]}},
                            {"name": "update_site", "description": "Update site", "inputSchema": {"type": "object", "properties": {"site_id": {"type": "string"}, "name": {"type": "string"}, "slug": {"type": "string"}, "theme_slug": {"type": "string"}}, "required": ["site_id"]}},
                            {"name": "delete_site", "description": "Soft delete a site (can be restored later)", "inputSchema": {"type": "object", "properties": {"site_id": {"type": "string"}}, "required": ["site_id"]}},
                            {"name": "list_pages", "description": "List pages", "inputSchema": {"type": "object", "properties": {"site_id": {"type": "string"}}, "required": ["site_id"]}},
                            {"name": "create_page", "description": "Create page", "inputSchema": {"type": "object", "properties": {"site_id": {"type": "string"}, "title": {"type": "string"}, "slug": {"type": "string"}, "is_published": {"type": "boolean"}}, "required": ["site_id", "title", "slug"]}},
                            {"name": "get_page_content", "description": "Get page content", "inputSchema": {"type": "object", "properties": {"site_id": {"type": "string"}, "page_id": {"type": "string"}}, "required": ["site_id", "page_id"]}},
                            {"name": "update_page_content", "description": "Update content", "inputSchema": {"type": "object", "properties": {"site_id": {"type": "string"}, "page_id": {"type": "string"}, "section_type": {"type": "string"}, "content": {"type": "string"}}, "required": ["site_id", "page_id", "section_type", "content"]}},
                            {"name": "update_page", "description": "Update page", "inputSchema": {"type": "object", "properties": {"page_id": {"type": "string"}, "title": {"type": "string"}, "slug": {"type": "string"}, "is_published": {"type": "boolean"}}, "required": ["page_id"]}},
                            {"name": "delete_page", "description": "Soft delete a page (can be restored later)", "inputSchema": {"type": "object", "properties": {"page_id": {"type": "string"}}, "required": ["page_id"]}},
                            {"name": "reorder_sections", "description": "Reorder content sections by swapping two sections", "inputSchema": {"type": "object", "properties": {"site_id": {"type": "string"}, "page_id": {"type": "string"}, "section_id_1": {"type": "string", "description": "First section ID to swap"}, "section_id_2": {"type": "string", "description": "Second section ID to swap"}}, "required": ["site_id", "page_id", "section_id_1", "section_id_2"]}},
                            {"name": "set_section_order", "description": "Set absolute order of all sections in one operation", "inputSchema": {"type": "object", "properties": {"site_id": {"type": "string"}, "page_id": {"type": "string"}, "section_order": {"type": "array", "items": {"type": "string"}, "description": "Array of section types in desired order (e.g., ['hero', 'body', 'oasis', 'cta'])"}}, "required": ["site_id", "page_id", "section_order"]}},
                            {"name": "delete_section", "description": "Soft delete a content section by section type (can be restored later)", "inputSchema": {"type": "object", "properties": {"site_id": {"type": "string"}, "page_id": {"type": "string"}, "section_type": {"type": "string", "description": "Section type to delete (e.g., hero, body, cta)"}}, "required": ["site_id", "page_id", "section_type"]}},
                            {"name": "restore_site", "description": "Restore a soft-deleted site", "inputSchema": {"type": "object", "properties": {"site_id": {"type": "string"}}, "required": ["site_id"]}},
                            {"name": "restore_page", "description": "Restore a soft-deleted page", "inputSchema": {"type": "object", "properties": {"page_id": {"type": "string"}}, "required": ["page_id"]}},
                            {"name": "restore_section", "description": "Restore a soft-deleted section by section type", "inputSchema": {"type": "object", "properties": {"site_id": {"type": "string"}, "page_id": {"type": "string"}, "section_type": {"type": "string", "description": "Section type to restore (e.g., hero, body, cta)"}}, "required": ["site_id", "page_id", "section_type"]}},
                            {"name": "list_themes", "description": "List themes", "inputSchema": {"type": "object", "properties": {}}},
                            {"name": "apply_theme", "description": "Apply theme", "inputSchema": {"type": "object", "properties": {"site_id": {"type": "string"}, "theme_slug": {"type": "string"}}, "required": ["site_id", "theme_slug"]}},
                        ]
                        return JSONResponse(content={"jsonrpc": "2.0", "id": message.get("id"), "result": {"tools": tools}})
                    
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
                        tool_name = params.get("name")
                        args = params.get("arguments", {})
                        
                        print(f"Tool call: {tool_name} with args: {args}")
                        
                        # Make actual API call to backend
                        try:
                            import httpx
                            async with httpx.AsyncClient(follow_redirects=True) as client:
                                headers = {"Authorization": f"Bearer {auth_header[7:] if auth_header.startswith('Bearer ') else ''}"}
                                base_url = "http://backend:8000/api"
                                
                                if tool_name == "list_sites":
                                    response = await client.get(f"{base_url}/sites", headers=headers)
                                    if response.status_code == 200:
                                        sites = response.json()
                                        if sites:
                                            content_text = "Your sites:\n" + "\n".join(
                                                f"- {s['name']} (slug: {s['slug']}, theme: {s.get('theme_slug', 'default')}, ID: {s['id']})"
                                                for s in sites
                                            )
                                        else:
                                            content_text = "No sites found. Create one with create_site."
                                    else:
                                        content_text = f"Error: {response.status_code} - {response.text}"
                                
                                elif tool_name == "create_site":
                                    response = await client.post(
                                        f"{base_url}/sites",
                                        headers=headers,
                                        json={
                                            "name": args["name"],
                                            "slug": args["slug"],
                                            "theme_slug": args.get("theme_slug", "default")
                                        }
                                    )
                                    if response.status_code in (200, 201):
                                        site = response.json()
                                        content_text = f"Site '{site['name']}' created successfully with slug '{site['slug']}' (ID: {site['id']})"
                                    else:
                                        content_text = f"Error creating site: {response.status_code} - {response.text}"
                                
                                elif tool_name == "get_site_info":
                                    site_id = args["site_id"]
                                    response = await client.get(f"{base_url}/sites/{site_id}", headers=headers)
                                    if response.status_code == 200:
                                        site = response.json()
                                        # Get pages
                                        pages_resp = await client.get(f"{base_url}/sites/{site_id}/pages", headers=headers)
                                        pages = pages_resp.json() if pages_resp.status_code == 200 else []
                                        pages_text = "\n".join(f"  - {p['title']} (slug: {p['slug']})" for p in pages) if pages else "  No pages"
                                        content_text = f"Site: {site['name']}\nSlug: {site['slug']}\nTheme: {site.get('theme_slug', 'default')}\n\nPages:\n{pages_text}"
                                    else:
                                        content_text = f"Error: {response.status_code}"
                                
                                elif tool_name == "list_pages":
                                    site_id = args["site_id"]
                                    response = await client.get(f"{base_url}/sites/{site_id}/pages", headers=headers)
                                    if response.status_code == 200:
                                        pages = response.json()
                                        if pages:
                                            content_text = "Pages:\n" + "\n".join(
                                                f"- {p['title']} (slug: {p['slug']}, published: {p['is_published']})"
                                                for p in pages
                                            )
                                        else:
                                            content_text = "No pages found for this site."
                                    else:
                                        content_text = f"Error: {response.status_code}"
                                
                                elif tool_name == "create_page":
                                    site_id = args["site_id"]
                                    response = await client.post(
                                        f"{base_url}/sites/{site_id}/pages",
                                        headers=headers,
                                        json={
                                            "title": args["title"],
                                            "slug": args["slug"],
                                            "is_published": args.get("is_published", False)
                                        }
                                    )
                                    if response.status_code in (200, 201):
                                        page = response.json()
                                        content_text = f"Page '{page['title']}' created successfully"
                                    else:
                                        content_text = f"Error: {response.status_code} - {response.text}"
                                
                                elif tool_name == "apply_theme":
                                    site_id = args["site_id"]
                                    theme_slug = args["theme_slug"]
                                    
                                    # If site_id looks like a slug (not UUID), try to get the UUID first
                                    if len(site_id) < 36 or "-" not in site_id:
                                        # Try to find site by slug
                                        sites_resp = await client.get(f"{base_url}/sites/", headers=headers)
                                        if sites_resp.status_code == 200:
                                            sites = sites_resp.json()
                                            for s in sites:
                                                if s["slug"] == site_id:
                                                    site_id = s["id"]
                                                    break
                                    
                                    response = await client.patch(
                                        f"{base_url}/sites/{site_id}",
                                        headers=headers,
                                        json={"theme_slug": theme_slug}
                                    )
                                    if response.status_code == 200:
                                        content_text = f"Theme '{theme_slug}' applied successfully to site"
                                    else:
                                        content_text = f"Error applying theme: {response.status_code} - {response.text}"
                                
                                elif tool_name == "list_themes":
                                    response = await client.get(f"{base_url}/themes/", headers=headers)
                                    if response.status_code == 200:
                                        themes = response.json()
                                        if themes:
                                            content_text = "Available themes:\n" + "\n".join(
                                                f"- {t['slug']} ({t.get('name', 'No name')})"
                                                for t in themes
                                            )
                                        else:
                                            content_text = "No themes available."
                                    else:
                                        content_text = f"Error listing themes: {response.status_code}"
                                
                                elif tool_name == "get_page_content":
                                    site_id = args["site_id"]
                                    page_id = args["page_id"]
                                    
                                    # Convert site slug to UUID if needed
                                    if len(site_id) < 36 or "-" not in site_id:
                                        sites_resp = await client.get(f"{base_url}/sites/", headers=headers)
                                        if sites_resp.status_code == 200:
                                            sites = sites_resp.json()
                                            for s in sites:
                                                if s["slug"] == site_id:
                                                    site_id = s["id"]
                                                    break
                                    
                                    # Get pages for this specific site
                                    pages_resp = await client.get(f"{base_url}/sites/{site_id}/pages", headers=headers)
                                    if pages_resp.status_code == 200:
                                        pages = pages_resp.json()
                                        page_found = False
                                        for page in pages:
                                            if page['id'] == page_id or page['slug'] == page_id:
                                                content_resp = await client.get(f"{base_url}/sites/{site_id}/pages/{page['id']}/content", headers=headers)
                                                if content_resp.status_code == 200:
                                                    content_sections = content_resp.json()
                                                    if content_sections:
                                                        content_text = "Content sections:\n" + "\n".join(
                                                            f"- {c['section_type']}: {c['content'][:100]}..."
                                                            for c in content_sections
                                                        )
                                                    else:
                                                        content_text = "No content sections found."
                                                else:
                                                    content_text = f"Error fetching content: {content_resp.status_code}"
                                                page_found = True
                                                break
                                        if not page_found:
                                            content_text = f"Page not found: {page_id}"
                                    else:
                                        content_text = f"Error: Could not find site {site_id}"
                                
                                elif tool_name == "update_page_content":
                                    site_id = args["site_id"]
                                    page_id = args["page_id"]
                                    section_type = args["section_type"]
                                    content = args["content"]
                                    
                                    # Convert site slug to UUID if needed
                                    if len(site_id) < 36 or "-" not in site_id:
                                        sites_resp = await client.get(f"{base_url}/sites/", headers=headers)
                                        if sites_resp.status_code == 200:
                                            sites = sites_resp.json()
                                            for s in sites:
                                                if s["slug"] == site_id:
                                                    site_id = s["id"]
                                                    break
                                    
                                    # Get pages for this specific site
                                    pages_resp = await client.get(f"{base_url}/sites/{site_id}/pages", headers=headers)
                                    if pages_resp.status_code == 200:
                                        pages = pages_resp.json()
                                        page_found = False
                                        for page in pages:
                                            if page['id'] == page_id or page['slug'] == page_id:
                                                # Get existing content sections
                                                content_resp = await client.get(f"{base_url}/sites/{site_id}/pages/{page['id']}/content", headers=headers)
                                                if content_resp.status_code == 200:
                                                    sections = content_resp.json()
                                                    # Find the section to update
                                                    for section in sections:
                                                        if section['section_type'] == section_type:
                                                            # Update the section
                                                            update_resp = await client.patch(
                                                                f"{base_url}/sites/{site_id}/pages/{page['id']}/content/{section['id']}",
                                                                headers=headers,
                                                                json={"content": content}
                                                            )
                                                            if update_resp.status_code == 200:
                                                                content_text = f"Section '{section_type}' updated successfully"
                                                            else:
                                                                content_text = f"Error updating section: {update_resp.status_code}"
                                                            page_found = True
                                                            break
                                                    
                                                    if not page_found:
                                                        # Section not found, create new one
                                                        create_resp = await client.post(
                                                            f"{base_url}/sites/{site_id}/pages/{page['id']}/content",
                                                            headers=headers,
                                                            json={
                                                                "section_type": section_type,
                                                                "content": content,
                                                                "order": len(sections)
                                                            }
                                                        )
                                                        if create_resp.status_code in (200, 201):
                                                            content_text = f"Section '{section_type}' created successfully"
                                                        else:
                                                            content_text = f"Error creating section: {create_resp.status_code}"
                                                else:
                                                    content_text = f"Error fetching content: {content_resp.status_code}"
                                                break
                                        if not page_found:
                                            content_text = f"Page not found: {page_id}"
                                    else:
                                        content_text = f"Error: Could not find site {site_id}"
                                
                                elif tool_name == "update_page":
                                    page_id = args["page_id"]
                                    update_data = {}
                                    if "title" in args:
                                        update_data["title"] = args["title"]
                                    if "slug" in args:
                                        update_data["slug"] = args["slug"]
                                    if "is_published" in args:
                                        update_data["is_published"] = args["is_published"]
                                    
                                    # Find site and update page
                                    sites_resp = await client.get(f"{base_url}/sites/", headers=headers)
                                    content_text = f"Error: Could not find page {page_id}"
                                    page_updated = False
                                    if sites_resp.status_code == 200:
                                        sites = sites_resp.json()
                                        for site in sites:
                                            if page_updated:
                                                break
                                            pages_resp = await client.get(f"{base_url}/sites/{site['id']}/pages", headers=headers)
                                            if pages_resp.status_code == 200:
                                                pages = pages_resp.json()
                                                for page in pages:
                                                    if page['id'] == page_id or page['slug'] == page_id:
                                                        resp = await client.patch(
                                                            f"{base_url}/sites/{site['id']}/pages/{page['id']}",
                                                            headers=headers,
                                                            json=update_data
                                                        )
                                                        if resp.status_code == 200:
                                                            content_text = f"Page updated successfully"
                                                        else:
                                                            content_text = f"Error: {resp.status_code}"
                                                        page_updated = True
                                                        break
                                
                                elif tool_name == "delete_page":
                                    page_id = args["page_id"]
                                    sites_resp = await client.get(f"{base_url}/sites/", headers=headers)
                                    content_text = f"Error: Could not find page {page_id}"
                                    page_deleted = False
                                    if sites_resp.status_code == 200:
                                        sites = sites_resp.json()
                                        for site in sites:
                                            if page_deleted:
                                                break
                                            pages_resp = await client.get(f"{base_url}/sites/{site['id']}/pages", headers=headers)
                                            if pages_resp.status_code == 200:
                                                pages = pages_resp.json()
                                                for page in pages:
                                                    if page['id'] == page_id or page['slug'] == page_id:
                                                        resp = await client.delete(
                                                            f"{base_url}/sites/{site['id']}/pages/{page['id']}",
                                                            headers=headers
                                                        )
                                                        if resp.status_code in (200, 204):
                                                            content_text = f"Page deleted successfully"
                                                        else:
                                                            content_text = f"Error: {resp.status_code}"
                                                        page_deleted = True
                                                        break
                                
                                elif tool_name == "reorder_sections":
                                    site_id = args["site_id"]
                                    page_id = args["page_id"]
                                    section_id_1 = args["section_id_1"]
                                    section_id_2 = args["section_id_2"]
                                    
                                    # Convert site slug to UUID if needed
                                    if len(site_id) < 36 or "-" not in site_id:
                                        sites_resp = await client.get(f"{base_url}/sites/", headers=headers)
                                        if sites_resp.status_code == 200:
                                            sites = sites_resp.json()
                                            for s in sites:
                                                if s["slug"] == site_id:
                                                    site_id = s["id"]
                                                    break
                                    
                                    # Get pages for this specific site
                                    pages_resp = await client.get(f"{base_url}/sites/{site_id}/pages", headers=headers)
                                    if pages_resp.status_code == 200:
                                        pages = pages_resp.json()
                                        page_found = False
                                        for page in pages:
                                            if page['id'] == page_id or page['slug'] == page_id:
                                                # Get current content to find orders
                                                content_resp = await client.get(
                                                    f"{base_url}/sites/{site_id}/pages/{page['id']}/content",
                                                    headers=headers
                                                )
                                                if content_resp.status_code == 200:
                                                    sections = content_resp.json()
                                                    
                                                    # Find sections by ID or type
                                                    section1 = next((s for s in sections if s['id'] == section_id_1 or s['section_type'] == section_id_1), None)
                                                    section2 = next((s for s in sections if s['id'] == section_id_2 or s['section_type'] == section_id_2), None)
                                                    
                                                    if section1 and section2:
                                                        # Swap orders
                                                        order1 = section1['order']
                                                        order2 = section2['order']
                                                        
                                                        # Update both sections
                                                        resp1 = await client.patch(
                                                            f"{base_url}/sites/{site_id}/pages/{page['id']}/content/{section1['id']}",
                                                            headers=headers,
                                                            json={"order": order2}
                                                        )
                                                        resp2 = await client.patch(
                                                            f"{base_url}/sites/{site_id}/pages/{page['id']}/content/{section2['id']}",
                                                            headers=headers,
                                                            json={"order": order1}
                                                        )
                                                        
                                                        if resp1.status_code == 200 and resp2.status_code == 200:
                                                            content_text = f"Sections reordered successfully"
                                                        else:
                                                            content_text = f"Error reordering sections: {resp1.status_code}, {resp2.status_code}"
                                                    else:
                                                        content_text = f"Error: One or both sections not found"
                                                else:
                                                    content_text = f"Error fetching content: {content_resp.status_code}"
                                                page_found = True
                                                break
                                        if not page_found:
                                            content_text = f"Page not found: {page_id}"
                                    else:
                                        content_text = f"Error: Could not find site {site_id}"
                                
                                elif tool_name == "set_section_order":
                                    site_id = args["site_id"]
                                    page_id = args["page_id"]
                                    section_order = args["section_order"]
                                    
                                    # Convert site slug to UUID if needed
                                    if len(site_id) < 36 or "-" not in site_id:
                                        sites_resp = await client.get(f"{base_url}/sites/", headers=headers)
                                        if sites_resp.status_code == 200:
                                            sites = sites_resp.json()
                                            for s in sites:
                                                if s["slug"] == site_id:
                                                    site_id = s["id"]
                                                    break
                                    
                                    # Get pages for this specific site
                                    pages_resp = await client.get(f"{base_url}/sites/{site_id}/pages", headers=headers)
                                    if pages_resp.status_code == 200:
                                        pages = pages_resp.json()
                                        page_found = False
                                        for page in pages:
                                            if page['id'] == page_id or page['slug'] == page_id:
                                                # Get current content sections
                                                content_resp = await client.get(f"{base_url}/sites/{site_id}/pages/{page['id']}/content", headers=headers)
                                                if content_resp.status_code == 200:
                                                    sections = content_resp.json()
                                                    
                                                    # Create a map of section_type to section_id
                                                    section_map = {s['section_type']: s['id'] for s in sections}
                                                    
                                                    # Update each section's order based on the desired order
                                                    all_updated = True
                                                    for idx, section_type in enumerate(section_order):
                                                        if section_type in section_map:
                                                            section_id = section_map[section_type]
                                                            resp = await client.patch(
                                                                f"{base_url}/sites/{site_id}/pages/{page['id']}/content/{section_id}",
                                                                headers=headers,
                                                                json={"order": idx}
                                                            )
                                                            if resp.status_code != 200:
                                                                all_updated = False
                                                                break
                                                    
                                                    if all_updated:
                                                        content_text = f"Sections reordered successfully: {' → '.join(section_order)}"
                                                    else:
                                                        content_text = "Error: Failed to update some sections"
                                                else:
                                                    content_text = f"Error fetching content: {content_resp.status_code}"
                                                page_found = True
                                                break
                                        if not page_found:
                                            content_text = f"Page not found: {page_id}"
                                    else:
                                        content_text = f"Error: Could not find site {site_id}"
                                
                                elif tool_name == "update_site":
                                    site_id = args["site_id"]
                                    update_data = {}
                                    if "name" in args:
                                        update_data["name"] = args["name"]
                                    if "slug" in args:
                                        update_data["slug"] = args["slug"]
                                    if "theme_slug" in args:
                                        update_data["theme_slug"] = args["theme_slug"]
                                    
                                    # Convert slug to UUID if needed
                                    if len(site_id) < 36 or "-" not in site_id:
                                        sites_resp = await client.get(f"{base_url}/sites/", headers=headers)
                                        if sites_resp.status_code == 200:
                                            sites = sites_resp.json()
                                            for s in sites:
                                                if s["slug"] == site_id:
                                                    site_id = s["id"]
                                                    break
                                    
                                    response = await client.patch(
                                        f"{base_url}/sites/{site_id}",
                                        headers=headers,
                                        json=update_data
                                    )
                                    if response.status_code == 200:
                                        content_text = f"Site updated successfully"
                                    else:
                                        content_text = f"Error updating site: {response.status_code} - {response.text}"
                                
                                elif tool_name == "delete_site":
                                    site_id = args["site_id"]
                                    
                                    # Convert slug to UUID if needed
                                    if len(site_id) < 36 or "-" not in site_id:
                                        sites_resp = await client.get(f"{base_url}/sites/", headers=headers)
                                        if sites_resp.status_code == 200:
                                            sites = sites_resp.json()
                                            for s in sites:
                                                if s["slug"] == site_id:
                                                    site_id = s["id"]
                                                    break
                                    
                                    response = await client.delete(
                                        f"{base_url}/sites/{site_id}",
                                        headers=headers
                                    )
                                    if response.status_code in (200, 204):
                                        content_text = f"Site deleted successfully"
                                    else:
                                        content_text = f"Error deleting site: {response.status_code} - {response.text}"
                                
                                elif tool_name == "restore_site":
                                    site_id = args["site_id"]
                                    
                                    # Convert slug to UUID if needed
                                    if len(site_id) < 36 or "-" not in site_id:
                                        sites_resp = await client.get(f"{base_url}/sites/?include_deleted=true", headers=headers)
                                        if sites_resp.status_code == 200:
                                            sites = sites_resp.json()
                                            for s in sites:
                                                if s["slug"] == site_id:
                                                    site_id = s["id"]
                                                    break
                                    
                                    response = await client.patch(
                                        f"{base_url}/sites/{site_id}",
                                        headers=headers,
                                        json={"is_deleted": False, "deleted_at": None}
                                    )
                                    if response.status_code == 200:
                                        content_text = f"Site restored successfully"
                                    else:
                                        content_text = f"Error restoring site: {response.status_code}"
                                
                                elif tool_name == "restore_page":
                                    page_id = args["page_id"]
                                    sites_resp = await client.get(f"{base_url}/sites/?include_deleted=true", headers=headers)
                                    content_text = f"Error: Could not find page {page_id}"
                                    page_restored = False
                                    
                                    if sites_resp.status_code == 200:
                                        sites = sites_resp.json()
                                        for site in sites:
                                            if page_restored:
                                                break
                                            pages_resp = await client.get(f"{base_url}/sites/{site['id']}/pages?include_deleted=true", headers=headers)
                                            if pages_resp.status_code == 200:
                                                pages = pages_resp.json()
                                                for page in pages:
                                                    if page['id'] == page_id or page['slug'] == page_id:
                                                        resp = await client.patch(
                                                            f"{base_url}/sites/{site['id']}/pages/{page['id']}",
                                                            headers=headers,
                                                            json={"is_deleted": False, "deleted_at": None}
                                                        )
                                                        if resp.status_code == 200:
                                                            content_text = f"Page restored successfully"
                                                        else:
                                                            content_text = f"Error: {resp.status_code}"
                                                        page_restored = True
                                                        break
                                
                                elif tool_name == "delete_section":
                                    site_id = args["site_id"]
                                    page_id = args["page_id"]
                                    section_type = args["section_type"]
                                    
                                    # Convert site slug to UUID if needed
                                    if len(site_id) < 36 or "-" not in site_id:
                                        sites_resp = await client.get(f"{base_url}/sites/", headers=headers)
                                        if sites_resp.status_code == 200:
                                            sites = sites_resp.json()
                                            for s in sites:
                                                if s["slug"] == site_id:
                                                    site_id = s["id"]
                                                    break
                                    
                                    # Get pages for this specific site
                                    pages_resp = await client.get(f"{base_url}/sites/{site_id}/pages", headers=headers)
                                    if pages_resp.status_code == 200:
                                        pages = pages_resp.json()
                                        page_found = False
                                        for page in pages:
                                            if page['id'] == page_id or page['slug'] == page_id:
                                                # Get existing content sections
                                                content_resp = await client.get(f"{base_url}/sites/{site_id}/pages/{page['id']}/content", headers=headers)
                                                if content_resp.status_code == 200:
                                                    sections = content_resp.json()
                                                    # Find the section to delete
                                                    for section in sections:
                                                        if section['section_type'] == section_type:
                                                            # Delete the section
                                                            delete_resp = await client.delete(
                                                                f"{base_url}/sites/{site_id}/pages/{page['id']}/content/{section['id']}",
                                                                headers=headers
                                                            )
                                                            if delete_resp.status_code in (200, 204):
                                                                content_text = f"Section '{section_type}' deleted successfully"
                                                            else:
                                                                content_text = f"Error deleting section: {delete_resp.status_code}"
                                                            page_found = True
                                                            break
                                                    
                                                    if not page_found:
                                                        content_text = f"Section '{section_type}' not found"
                                                else:
                                                    content_text = f"Error fetching content: {content_resp.status_code}"
                                                break
                                        if not page_found:
                                            content_text = f"Page not found: {page_id}"
                                    else:
                                        content_text = f"Error: Could not find site {site_id}"
                                
                                elif tool_name == "restore_section":
                                    site_id = args["site_id"]
                                    page_id = args["page_id"]
                                    section_type = args["section_type"]
                                    
                                    # Convert site slug to UUID if needed
                                    if len(site_id) < 36 or "-" not in site_id:
                                        sites_resp = await client.get(f"{base_url}/sites/?include_deleted=true", headers=headers)
                                        if sites_resp.status_code == 200:
                                            sites = sites_resp.json()
                                            for s in sites:
                                                if s["slug"] == site_id:
                                                    site_id = s["id"]
                                                    break
                                    
                                    # Get pages for this specific site (including deleted)
                                    pages_resp = await client.get(f"{base_url}/sites/{site_id}/pages?include_deleted=true", headers=headers)
                                    if pages_resp.status_code == 200:
                                        pages = pages_resp.json()
                                        page_found = False
                                        for page in pages:
                                            if page['id'] == page_id or page['slug'] == page_id:
                                                # Get content sections (including deleted)
                                                content_resp = await client.get(f"{base_url}/sites/{site_id}/pages/{page['id']}/content?include_deleted=true", headers=headers)
                                                if content_resp.status_code == 200:
                                                    sections = content_resp.json()
                                                    # Find the deleted section
                                                    for section in sections:
                                                        if section['section_type'] == section_type and section.get('is_deleted'):
                                                            # Restore the section
                                                            restore_resp = await client.patch(
                                                                f"{base_url}/sites/{site_id}/pages/{page['id']}/content/{section['id']}",
                                                                headers=headers,
                                                                json={"is_deleted": False, "deleted_at": None}
                                                            )
                                                            if restore_resp.status_code == 200:
                                                                content_text = f"Section '{section_type}' restored successfully"
                                                            else:
                                                                content_text = f"Error restoring section: {restore_resp.status_code}"
                                                            page_found = True
                                                            break
                                                    
                                                    if not page_found:
                                                        content_text = f"Deleted section '{section_type}' not found"
                                                else:
                                                    content_text = f"Error fetching content: {content_resp.status_code}"
                                                break
                                        if not page_found:
                                            content_text = f"Page not found: {page_id}"
                                    else:
                                        content_text = f"Error: Could not find site {site_id}"
                                
                                else:
                                    content_text = f"Tool {tool_name} executed with args: {args}"
                                
                                return JSONResponse(content={
                                    "jsonrpc": "2.0",
                                    "id": message.get("id"),
                                    "result": {
                                        "content": [{"type": "text", "text": content_text}]
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
    """Return the canonical list of MCP tools."""
    return [
        {"name": "list_sites", "description": "List all sites for the authenticated user", "inputSchema": {"type": "object", "properties": {}}},
        {"name": "create_site", "description": "Create a new site with name and slug", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "slug": {"type": "string"}, "theme_slug": {"type": "string"}}, "required": ["name", "slug"]}},
        {"name": "get_site_info", "description": "Get detailed information about a site including pages and theme", "inputSchema": {"type": "object", "properties": {"site_id": {"type": "string"}}, "required": ["site_id"]}},
        {"name": "describe_site", "description": "Get a full structured description of a site: theme, all pages, section types and their draft content", "inputSchema": {"type": "object", "properties": {"site_id": {"type": "string"}}, "required": ["site_id"]}},
        {"name": "update_site", "description": "Update site name, slug, or theme", "inputSchema": {"type": "object", "properties": {"site_id": {"type": "string"}, "name": {"type": "string"}, "slug": {"type": "string"}, "theme_slug": {"type": "string"}}, "required": ["site_id"]}},
        {"name": "delete_site", "description": "Soft delete a site", "inputSchema": {"type": "object", "properties": {"site_id": {"type": "string"}}, "required": ["site_id"]}},
        {"name": "list_pages", "description": "List all pages for a site", "inputSchema": {"type": "object", "properties": {"site_id": {"type": "string"}}, "required": ["site_id"]}},
        {"name": "create_page", "description": "Create a new page on a site", "inputSchema": {"type": "object", "properties": {"site_id": {"type": "string"}, "title": {"type": "string"}, "slug": {"type": "string"}, "is_published": {"type": "boolean"}}, "required": ["site_id", "title", "slug"]}},
        {"name": "update_page", "description": "Update page title, slug, or publish status", "inputSchema": {"type": "object", "properties": {"site_id": {"type": "string"}, "page_id": {"type": "string"}, "title": {"type": "string"}, "slug": {"type": "string"}, "is_published": {"type": "boolean"}}, "required": ["site_id", "page_id"]}},
        {"name": "delete_page", "description": "Soft delete a page", "inputSchema": {"type": "object", "properties": {"site_id": {"type": "string"}, "page_id": {"type": "string"}}, "required": ["site_id", "page_id"]}},
        {"name": "publish_page", "description": "Publish all draft content on a page (makes changes live)", "inputSchema": {"type": "object", "properties": {"site_id": {"type": "string"}, "page_id": {"type": "string"}}, "required": ["site_id", "page_id"]}},
        {"name": "get_page_content", "description": "Get content sections for a page (returns draft content)", "inputSchema": {"type": "object", "properties": {"site_id": {"type": "string"}, "page_id": {"type": "string"}}, "required": ["site_id", "page_id"]}},
        {"name": "update_section", "description": "Create or update a content section by type. Pass structured JSON in the content field.", "inputSchema": {"type": "object", "properties": {"site_id": {"type": "string"}, "page_id": {"type": "string"}, "section_type": {"type": "string"}, "content": {"type": "object"}, "order": {"type": "integer"}}, "required": ["site_id", "page_id", "section_type", "content"]}},
        {"name": "generate_section", "description": "Generate a complete content section from a text description using AI defaults", "inputSchema": {"type": "object", "properties": {"site_id": {"type": "string"}, "page_id": {"type": "string"}, "section_type": {"type": "string"}, "description": {"type": "string"}}, "required": ["site_id", "page_id", "section_type", "description"]}},
        {"name": "delete_section", "description": "Soft delete a content section by type", "inputSchema": {"type": "object", "properties": {"site_id": {"type": "string"}, "page_id": {"type": "string"}, "section_type": {"type": "string"}}, "required": ["site_id", "page_id", "section_type"]}},
        {"name": "list_themes", "description": "List available themes", "inputSchema": {"type": "object", "properties": {}}},
        {"name": "apply_theme", "description": "Apply a theme to a site", "inputSchema": {"type": "object", "properties": {"site_id": {"type": "string"}, "theme_slug": {"type": "string"}}, "required": ["site_id", "theme_slug"]}},
    ]


async def _get_mcp_server_for_client(client_id: str) -> MCPServer:
    """Look up MCP client by ID and return an MCPServer configured with its token."""
    api_url = os.getenv("API_URL", "http://backend:8000/api")
    async with get_db_session() as db:
        result = await db.execute(select(MCPClient).where(MCPClient.id == client_id))
        client = result.scalar_one_or_none()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        return MCPServer(api_url, client.token)


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
