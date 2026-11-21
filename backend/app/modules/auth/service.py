"""Authentication business operations, shared by all API clients."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.modules.auth.models import AuthSession, PlatformRole, User
from app.modules.auth.roles import grant_registration_role


class DuplicateEmailError(Exception):
    """Raised when a normalized email is already registered."""


class InvalidCredentialsError(Exception):
    """Raised for unknown, invalid, or inactive account credentials."""


@dataclass(frozen=True)
class LoginResult:
    user: User
    access_token: str
    refresh_token: str
    expires_in: int


def normalize_email(email: str) -> str:
    return email.strip().lower()


def register_user(db: Session, email: str, password: str) -> User:
    normalized_email = normalize_email(email)
    member_role = db.get(PlatformRole, "member")
    if member_role is None:
        raise RuntimeError("Default member role is not configured.")

    user = User(
        email=normalized_email,
        password_hash=security.hash_password(password),
    )
    grant_registration_role(user, member_role)
    db.add(user)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        diag = getattr(exc.orig, "diag", None)
        if getattr(diag, "constraint_name", None) == "uq_users_email":
            raise DuplicateEmailError from exc
        raise

    db.refresh(user)
    return user


def login_user(db: Session, email: str, password: str) -> LoginResult:
    user = db.scalar(select(User).where(User.email == normalize_email(email)))
    if user is None:
        # Match the password-hash work for unknown accounts without revealing
        # whether the email exists through a fast response path.
        security.hash_password(password)
        raise InvalidCredentialsError

    password_matches = security.verify_password(password, user.password_hash)
    if not password_matches or not user.is_active:
        raise InvalidCredentialsError

    now = datetime.now(timezone.utc)
    refresh_token = security.generate_refresh_token()
    auth_session = AuthSession(
        id=uuid4(),
        user_id=user.id,
        token_hash=security.hash_refresh_token(refresh_token),
        family_id=uuid4(),
        expires_at=now + timedelta(days=settings.refresh_token_expire_days),
    )

    try:
        db.add(auth_session)
        db.flush()
        access_token = security.create_access_token(user.id, auth_session.id)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return LoginResult(
        user=user,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )
