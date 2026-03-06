import asyncio
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models.user import User
from src.schemas.user import Token, UserCreate, UserResponse
from src.services.auth import AuthService
from src.services.email import EmailService

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    # First, try to decode as JWT
    payload = AuthService.decode_access_token(token)
    if payload is not None:
        user_id_str = payload.get("sub")
        if user_id_str:
            try:
                user_id = UUID(user_id_str)
                result = await db.execute(select(User).where(User.id == user_id))
                user = result.scalar_one_or_none()
                if user:
                    return user
            except ValueError:
                pass

    # If JWT failed, check if it's an MCP client token
    # Import MCPClient model here to avoid circular imports
    from src.models import MCPClient

    result = await db.execute(select(MCPClient).where(MCPClient.token == token))
    mcp_client = result.scalar_one_or_none()
    if mcp_client:
        # Get the user associated with this MCP client
        result = await db.execute(select(User).where(User.id == mcp_client.user_id))
        user = result.scalar_one_or_none()
        if user:
            return user

    # If neither worked, raise 401
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    user_in: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )

    db_user = User(
        email=user_in.email,
        password_hash=AuthService.get_password_hash(user_in.password),
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    # Send welcome email (fire and forget — non-critical)
    asyncio.create_task(EmailService.send_welcome(str(db_user.email), str(db_user.email)))

    return db_user


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not AuthService.verify_password(
        form_data.password, str(user.password_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = AuthService.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user
