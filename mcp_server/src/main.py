import asyncio
import json
import os
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from uuid import UUID

import httpx
from fastapi import FastAPI, HTTPException, Depends, Request
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
    
    api_url = os.getenv("API_URL", "http://localhost:8000/api/v1")
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
    # Use the host from the request to support both localhost and ngrok
    scheme = request.url.scheme
    host = request.headers.get("host", "localhost:8000")
    base_url = f"{scheme}://{host}"
    
    return {
        "issuer": base_url,
        "authorization_endpoint": f"{base_url}/authorize",
        "token_endpoint": f"{base_url}/token",
        "response_types_supported": ["code"],
        "grant_types_supported": ["client_credentials"],
        "scopes_supported": ["mcp"],
        "token_endpoint_auth_methods_supported": ["client_secret_basic", "client_secret_post"]
    }


@app.get("/.well-known/oauth-protected-resource")
async def oauth_protected_resource(request: Request):
    """OAuth protected resource endpoint"""
    scheme = request.url.scheme
    host = request.headers.get("host", "localhost:8000")
    base_url = f"{scheme}://{host}"
    
    return {
        "resource": base_url,
        "scopes_supported": ["mcp"]
    }


@app.get("/.well-known/oauth-protected-resource/mcp-sse/sse/{client_id}")
async def oauth_protected_resource_sse(client_id: str):
    """OAuth protected resource for SSE endpoint"""
    return {"endpoint": f"/mcp-sse/sse/{client_id}"}


@app.get("/authorize")
async def authorize(
    response_type: str = "code",
    client_id: str = None,
    redirect_uri: str = None,
    code_challenge: str = None,
    code_challenge_method: str = None,
    state: str = None,
    scope: str = None
):
    """OAuth authorization endpoint - for Claude Desktop"""
    # Claude Desktop expects a redirect to complete OAuth
    # Since we're using client credentials flow, we can redirect directly
    if redirect_uri and redirect_uri.startswith("https://claude.ai"):
        # Redirect back to Claude with success
        return RedirectResponse(
            url=f"{redirect_uri}?code=authorized&state={state}",
            status_code=302
        )
    
    # For other cases, return a simple success
    return {"status": "authorized", "code": "authorized"}


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
    
    client_id = data.get("client_id")
    client_secret = data.get("client_secret")
    
    # For now, accept any credentials with client_id=aicms-client
    if client_id == "aicms-client":
        # Return a token that Claude can use
        return {
            "access_token": client_secret or "dummy-token",  # Use the secret or a dummy token
            "token_type": "Bearer",
            "expires_in": 86400  # 24 hours
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


@app.post("/mcp/{client_id}")
async def mcp_endpoint(
    client_id: str,
    request: Dict[str, Any],
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """MCP protocol endpoint"""
    
    # Verify client belongs to user
    client = await db.get(MCPClient, client_id)
    if not client or client.user_id != UUID(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Process MCP request
    if not mcp_server:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MCP server not initialized"
        )
    
    # Get user's JWT token for backend API
    # In a real implementation, you'd generate a fresh token
    # For now, we'll use a placeholder
    user_token = "user-jwt-token-placeholder"
    
    # Temporarily set the token for this request
    mcp_server.api_token = user_token
    
    try:
        # Convert to MCP request format
        if request.get("method") == "tools/list":
            result = await mcp_server.handle_list_tools(request)
        elif request.get("method") == "tools/call":
            result = await mcp_server.handle_call_tool(request)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unknown MCP method"
            )
        
        return result.dict()
    
    finally:
        # Clear token
        mcp_server.api_token = None


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


# SSE endpoint for Claude Desktop
@app.api_route("/{client_id}", methods=["GET", "POST"])
async def sse_endpoint(client_id: str, request: Request):
    """SSE endpoint for Claude Desktop MCP connections"""
    
    # For POST requests, we need to handle them differently
    if request.method == "POST":
        # Claude might be trying to POST to establish connection
        # Return the SSE stream anyway
        pass
    
    print(f"SSE connection requested for client: {client_id}")
    
    # Verify client exists
    async with get_db_session() as db:
        result = await db.execute(select(MCPClient).where(MCPClient.id == client_id))
        client = result.scalar_one_or_none()
        if not client:
            print(f"Client {client_id} not found")
            raise HTTPException(status_code=404, detail="Client not found")
    
    print(f"Client {client_id} verified, establishing SSE connection")
    
    async def event_stream():
        """SSE event stream for MCP protocol"""
        print("Starting SSE event stream")
        
        # Create SSE transport
        sse_transport = SseServerTransport("/messages/")
        
        # Create MCP server
        server = Server("aicms-mcp-server")
        
        # Add some example tools
        @server.list_tools()
        async def list_tools():
            return {
                "tools": [
                    {
                        "name": "get_sites",
                        "description": "Get all sites for the user",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                ]
            }
        
        # Handle the MCP protocol properly
        async def handle_request(scope, receive, send):
            # This will be called by the SSE transport
            pass
        
        # For now, send initial connection event
        yield "event: connected\ndata: MCP server connected\n\n"
        
        # In a real implementation, we'd use sse_transport.connect_sse()
        # For now, we'll simulate the protocol
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "capabilities": {
                    "tools": {}
                }
            }
        }
        yield f"event: message\ndata: {json.dumps(init_message)}\n\n"
        
        # Keep connection alive with periodic pings
        try:
            while True:
                # Check if client is still connected
                if await request.is_disconnected():
                    print("Client disconnected")
                    break
                    
                # Send ping and wait
                yield "event: ping\ndata: ping\n\n"
                
                # Use a shorter sleep with more frequent disconnection checks
                for _ in range(6):  # 6 * 5 = 30 seconds total
                    await asyncio.sleep(5)
                    if await request.is_disconnected():
                        print("Client disconnected during wait")
                        return
        except asyncio.CancelledError:
            print("SSE connection cancelled")
        except Exception as e:
            print(f"SSE connection error: {e}")
        finally:
            print("Cleaning up SSE connection")
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


# Alternative SSE endpoint path that Claude might expect
@app.api_route("/mcp-sse/sse/{client_id}", methods=["GET", "POST"])
async def sse_endpoint_alt(client_id: str, request: Request):
    """Alternative SSE endpoint path for Claude Desktop"""
    return await sse_endpoint(client_id, request)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
