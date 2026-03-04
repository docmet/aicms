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


# SSE endpoint for Claude Desktop - supports both GET (SSE) and POST (Streamable HTTP)
@app.api_route("/sse/{client_id}", methods=["GET", "POST"])
async def sse_endpoint(client_id: str, request: Request):
    """SSE endpoint for Claude Desktop MCP connections - supports SSE and Streamable HTTP"""
    
    print(f"MCP connection requested for client: {client_id}, method: {request.method}")
    
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
        
        # If client wants SSE stream, return streaming response
        if "text/event-stream" in accept_header:
            print("Client requesting SSE stream via POST - Streamable HTTP mode")
        else:
            # Regular HTTP POST - handle as Streamable HTTP initialization
            print("Regular HTTP POST - Streamable HTTP initialization")
            body = await request.body()
            if body:
                print(f"Received POST body: {body}")
            
            # Generate session ID for Streamable HTTP
            session_id = str(uuid.uuid4())
            print(f"Generated session ID: {session_id}")
            
            # Return proper MCP initialization response
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {
                                "listChanged": True
                            }
                        },
                        "serverInfo": {
                            "name": "aicms-mcp-server",
                            "version": "1.0.0"
                        }
                    }
                },
                headers={
                    "Mcp-Session-Id": session_id
                }
            )
    
    print(f"Establishing SSE connection for {client_id}")
    
    async def event_stream():
        """SSE event stream for MCP protocol"""
        print("Starting SSE event stream")
        
        # According to MCP spec, first send an endpoint event
        # This tells the client where to send messages
        base_url = f"{request.url.scheme}://{request.headers.get('host', 'localhost:8000')}"
        message_endpoint = f"{base_url}/sse/{client_id}/messages"
        
        print(f"Sending endpoint event: {message_endpoint}")
        yield f"event: endpoint\ndata: {message_endpoint}\n\n"
        
        # Keep connection alive and wait for client messages
        try:
            count = 0
            while True:
                count += 1
                # Check if client is still connected
                if await request.is_disconnected():
                    print(f"Client disconnected after {count} cycles")
                    break
                    
                # Just keep the connection alive - client will POST to messages endpoint
                await asyncio.sleep(10)
                
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
@app.post("/sse/{client_id}/messages")
async def mcp_messages(client_id: str, request: Request):
    """Handle MCP protocol messages"""
    body = await request.body()
    print(f"Received message for {client_id}: {body}")
    
    # Parse the JSON-RPC message
    try:
        message = json.loads(body.decode())
        print(f"Parsed message: {message}")
        
        # Handle initialization
        if message.get("method") == "initialize":
            response = {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {
                            "listChanged": True
                        }
                    },
                    "serverInfo": {
                        "name": "aicms-mcp-server",
                        "version": "1.0.0"
                    }
                }
            }
            
            # Send the response via SSE (we'd need to store the SSE connection)
            # For now, just return the response
            return response
        
        # Handle list tools
        if message.get("method") == "tools/list":
            response = {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "result": {
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
            }
            return response
        
        # Handle other methods
        return {"jsonrpc": "2.0", "id": message.get("id"), "result": {}}
        
    except Exception as e:
        print(f"Error parsing message: {e}")
        return {"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
