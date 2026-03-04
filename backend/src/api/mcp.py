import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth import get_current_user
from src.database import get_db
from src.models import User

router = APIRouter(prefix="/mcp", tags=["mcp"])


@router.post("/register")
async def register_mcp_client(
    client_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Register a new MCP client - proxy to MCP server"""

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://mcp_server:8000/register",
            json={**client_data, "user_id": str(current_user.id)}
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json()
            )

    return response.json()


@router.get("/clients")
async def list_mcp_clients(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's MCP clients - proxy to MCP server"""

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://mcp_server:8000/clients",
            headers={"Authorization": f"Bearer {current_user.id}"}
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json()
            )

    return response.json()


@router.delete("/clients/{client_id}")
async def delete_mcp_client(
    client_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete MCP client - proxy to MCP server"""

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"http://mcp_server:8000/clients/{client_id}",
            headers={"Authorization": f"Bearer {current_user.id}"}
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json()
            )

    return response.json()
