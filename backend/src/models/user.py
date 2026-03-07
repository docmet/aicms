import uuid
from enum import StrEnum

from sqlalchemy import Boolean, Column, DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text

from src.database import Base


class UserPlan(StrEnum):
    free = "free"
    pro = "pro"
    agency = "agency"


# Site limits per plan
PLAN_SITE_LIMITS: dict[str, int] = {
    UserPlan.free: 1,
    UserPlan.pro: 3,
    UserPlan.agency: 15,
}


class User(Base):
    """User model for authentication and multi-tenancy."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    plan: UserPlan = Column(  # type: ignore[assignment]
        Enum(UserPlan, name="user_plan_enum"),
        nullable=False,
        server_default=UserPlan.free,
    )
    email_verified = Column(Boolean, nullable=False, server_default=text("false"), default=False)
    email_verification_token = Column(String(64), nullable=True, index=True)
    reset_token = Column(String(64), nullable=True, index=True)
    reset_token_expires_at = Column(DateTime(timezone=True), nullable=True)
    stripe_customer_id = Column(String(255), nullable=True, unique=True, index=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    sites = relationship("Site", back_populates="user", cascade="all, delete-orphan")
    wordpress_sites = relationship("WordPressSite", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, plan={self.plan})>"
