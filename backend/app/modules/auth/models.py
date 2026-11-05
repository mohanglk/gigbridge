from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "email = lower(btrim(email))",
            name="ck_users_email_normalized",
        ),
        UniqueConstraint("email", name="uq_users_email"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=func.true()
    )
    email_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    password_changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    role_grants: Mapped[list[UserPlatformRole]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    auth_sessions: Mapped[list[AuthSession]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    @validates("email")
    def normalize_email(self, _key: str, value: str) -> str:
        return value.strip().lower()


class PlatformRole(Base):
    __tablename__ = "platform_roles"
    __table_args__ = (
        CheckConstraint(
            "key <> 'admin' OR is_registration_assignable = false",
            name="ck_platform_roles_admin_not_registration_assignable",
        ),
    )

    key: Mapped[str] = mapped_column(String(32), primary_key=True)
    description: Mapped[str] = mapped_column(String(160), nullable=False)
    is_registration_assignable: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=func.false()
    )

    user_grants: Mapped[list[UserPlatformRole]] = relationship(
        back_populates="role",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class UserPlatformRole(Base):
    __tablename__ = "user_platform_roles"

    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role_key: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("platform_roles.key", ondelete="CASCADE"),
        primary_key=True,
    )
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user: Mapped[User] = relationship(back_populates="role_grants")
    role: Mapped[PlatformRole] = relationship(back_populates="user_grants")


class AuthSession(Base):
    """One refresh-token instance in a user's rotating session family."""

    __tablename__ = "auth_sessions"
    __table_args__ = (
        Index("ix_auth_sessions_user_id", "user_id"),
        Index("ix_auth_sessions_family_id", "family_id"),
        UniqueConstraint("token_hash", name="uq_auth_sessions_token_hash"),
        UniqueConstraint(
            "replaced_by_session_id",
            name="uq_auth_sessions_replaced_by_session_id",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    family_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), nullable=False, default=uuid4
    )
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    replaced_by_session_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey(
            "auth_sessions.id",
            name="fk_auth_sessions_replaced_by_session_id_auth_sessions",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    device_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)

    user: Mapped[User] = relationship(back_populates="auth_sessions")
    replacement_session: Mapped[AuthSession | None] = relationship(
        remote_side="AuthSession.id",
        foreign_keys=[replaced_by_session_id],
        uselist=False,
    )
