import asyncio
import secrets
from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models.user import User
from src.schemas.user import Token, UserCreate, UserResponse
from src.services.auth import AuthService
from src.services.email import EmailService

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

RESET_TOKEN_TTL_HOURS = 1
VERIFY_TOKEN_BYTES = 32


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
    from src.models import MCPClient

    result = await db.execute(select(MCPClient).where(MCPClient.token == token))
    mcp_client = result.scalar_one_or_none()
    if mcp_client:
        result = await db.execute(select(User).where(User.id == mcp_client.user_id))
        user = result.scalar_one_or_none()
        if user:
            return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


# ── Register ───────────────────────────────────────────────────────────────────


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )

    verification_token = secrets.token_urlsafe(VERIFY_TOKEN_BYTES)
    db_user = User(
        email=user_in.email,
        password_hash=AuthService.get_password_hash(user_in.password),
        email_verified=False,
        email_verification_token=verification_token,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    asyncio.create_task(
        EmailService.send_verification_email(str(db_user.email), verification_token)
    )
    return db_user


# ── Login ──────────────────────────────────────────────────────────────────────


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


class UpdateProfileRequest(BaseModel):
    name: str | None = None
    phone: str | None = None


@router.patch("/me", response_model=UserResponse)
async def update_me(
    body: UpdateProfileRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Update the current user's profile (name/phone — email requires admin)."""
    changed = False
    if body.name is not None:
        current_user.name = body.name  # type: ignore[assignment]
        changed = True
    if body.phone is not None:
        current_user.phone = body.phone  # type: ignore[assignment]
        changed = True
    if changed:
        db.add(current_user)
        await db.commit()
        await db.refresh(current_user)
    return current_user


# ── Email verification ─────────────────────────────────────────────────────────


class VerifyEmailRequest(BaseModel):
    token: str


@router.post("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(
    body: VerifyEmailRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    result = await db.execute(
        select(User).where(User.email_verification_token == body.token)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification link")

    user.email_verified = True  # type: ignore[assignment]
    user.email_verification_token = None  # type: ignore[assignment]
    db.add(user)
    await db.commit()
    return {"message": "Email verified"}


class ResendVerificationRequest(BaseModel):
    email: EmailStr


@router.post("/resend-verification", status_code=status.HTTP_200_OK)
async def resend_verification(
    body: ResendVerificationRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Resend verification email. Always returns 200 (avoids email enumeration)."""
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if user and not user.email_verified:  # type: ignore[truthy-bool]
        token = secrets.token_urlsafe(VERIFY_TOKEN_BYTES)
        user.email_verification_token = token  # type: ignore[assignment]
        db.add(user)
        await db.commit()
        asyncio.create_task(
            EmailService.send_verification_email(str(user.email), token)
        )

    return {"message": "If that email is registered and unverified, a new link was sent"}


# ── Password reset ─────────────────────────────────────────────────────────────


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    body: ForgotPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Generate a password reset token and email it. Always returns 200."""
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if user:
        token = secrets.token_urlsafe(VERIFY_TOKEN_BYTES)
        user.reset_token = token  # type: ignore[assignment]
        user.reset_token_expires_at = datetime.now(UTC) + timedelta(  # type: ignore[assignment]
            hours=RESET_TOKEN_TTL_HOURS
        )
        db.add(user)
        await db.commit()
        asyncio.create_task(EmailService.send_password_reset(str(user.email), token))

    return {"message": "If that email is registered, a reset link was sent"}


class ResetPasswordRequest(BaseModel):
    token: str
    password: str


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    body: ResetPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    result = await db.execute(select(User).where(User.reset_token == body.token))
    user = result.scalar_one_or_none()

    if not user or not user.reset_token_expires_at:  # type: ignore[truthy-bool]
        raise HTTPException(status_code=400, detail="Invalid or expired reset link")

    expires = user.reset_token_expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=UTC)
    if datetime.now(UTC) > expires:
        raise HTTPException(status_code=400, detail="Reset link has expired")

    if len(body.password) < 8:
        raise HTTPException(status_code=422, detail="Password must be at least 8 characters")

    user.password_hash = AuthService.get_password_hash(body.password)  # type: ignore[assignment]
    user.reset_token = None  # type: ignore[assignment]
    user.reset_token_expires_at = None  # type: ignore[assignment]
    db.add(user)
    await db.commit()
    return {"message": "Password updated"}
