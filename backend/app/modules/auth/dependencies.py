from datetime import datetime, timezone
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core import security
from app.core.database import get_db
from app.modules.auth.models import AuthSession, User

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(
        status_code=401,
        detail="Not authenticated.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None or credentials.scheme.casefold() != "bearer":
        raise unauthorized

    try:
        claims = security.verify_access_token(credentials.credentials)
        user_id = UUID(claims["sub"])
        session_id = UUID(claims["sid"])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError):
        raise unauthorized from None

    auth_session = db.get(AuthSession, session_id)
    now = datetime.now(timezone.utc)
    if (
        auth_session is None
        or auth_session.user_id != user_id
        or auth_session.revoked_at is not None
        or auth_session.expires_at <= now
    ):
        raise unauthorized

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise unauthorized
    return user
