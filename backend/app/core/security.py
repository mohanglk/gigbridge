"""Password and access-token helpers shared by all API clients."""

from datetime import datetime, timedelta, timezone
import base64
import binascii
import hashlib
import secrets
from typing import Any
from uuid import UUID, uuid4

import jwt
from argon2.exceptions import VerificationError
from pwdlib import PasswordHash
from pwdlib.exceptions import PwdlibError

from app.core.config import settings

JWT_ALGORITHM = "HS256"
ALLOWED_JWT_ALGORITHMS = (JWT_ALGORITHM,)
ACCESS_TOKEN_TYPE = "access"
MAX_PASSWORD_BYTES = 1024

_password_hasher = PasswordHash.recommended()


class SecurityConfigurationError(RuntimeError):
    """Raised when signing configuration is absent or unsafe."""


def hash_password(password: str) -> str:
    if not isinstance(password, str) or not password:
        raise ValueError("Password must not be empty.")
    if len(password.encode("utf-8")) > MAX_PASSWORD_BYTES:
        raise ValueError("Password is too long.")
    return _password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    if (
        not isinstance(password, str)
        or not password
        or len(password.encode("utf-8")) > MAX_PASSWORD_BYTES
        or not isinstance(password_hash, str)
        or not password_hash
    ):
        return False

    try:
        return _password_hasher.verify(password, password_hash)
    except (PwdlibError, VerificationError, ValueError):
        return False


def generate_refresh_token() -> str:
    """Return a high-entropy opaque token; persist only its hash."""
    return secrets.token_urlsafe(48)


def hash_refresh_token(refresh_token: str) -> str:
    if not isinstance(refresh_token, str) or not refresh_token:
        raise ValueError("Refresh token must not be empty.")
    return hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()


def _validated_signing_secret() -> bytes:
    if settings.jwt_algorithm not in ALLOWED_JWT_ALGORITHMS:
        raise SecurityConfigurationError("JWT algorithm is not supported.")

    configured_secret = settings.jwt_secret
    if configured_secret is None:
        raise SecurityConfigurationError("JWT signing secret is not configured.")

    secret = configured_secret.get_secret_value()
    placeholders = {
        "change-me",
        "changeme",
        "secret",
        "password",
        "your-secret-key",
        "replace-me",
        "development-secret",
    }
    if not secret or secret != secret.strip() or secret.casefold() in placeholders:
        raise SecurityConfigurationError(
            "JWT signing secret is missing or is a known placeholder."
        )

    # Require canonical, unpadded URL-safe Base64. This validates key format and
    # size only; it cannot establish how the key was generated or its entropy.
    try:
        key_material = base64.b64decode(
            secret + "=" * (-len(secret) % 4), altchars=b"-_", validate=True
        )
    except (binascii.Error, ValueError) as exc:
        raise SecurityConfigurationError(
            "JWT signing secret must be URL-safe Base64 encoded key material."
        ) from exc
    # Reject a simple constant encoding, but do not treat character counts or
    # these checks as evidence of entropy; generation remains an operator duty.
    if (
        base64.urlsafe_b64encode(key_material).decode("ascii").rstrip("=") != secret
        or len(key_material) < 32
        or len(set(key_material)) == 1
        or len(set(secret)) == 1
    ):
        raise SecurityConfigurationError(
            "JWT signing secret must encode at least 32 bytes of non-degenerate key material."
        )

    if not settings.jwt_issuer.strip() or not settings.jwt_audience.strip():
        raise SecurityConfigurationError("JWT issuer and audience must be configured.")

    return key_material


def create_access_token(subject: UUID | str, session_id: UUID | str) -> str:
    secret = _validated_signing_secret()
    subject_value = str(subject).strip()
    session_value = str(session_id).strip()
    if not subject_value or not session_value:
        raise ValueError("Token subject and session ID must not be empty.")

    issued_at = datetime.now(timezone.utc)
    expires_at = issued_at + timedelta(minutes=settings.access_token_expire_minutes)
    claims: dict[str, Any] = {
        "sub": subject_value,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": issued_at,
        "exp": expires_at,
        "jti": str(uuid4()),
        "token_type": ACCESS_TOKEN_TYPE,
        "sid": session_value,
    }
    return jwt.encode(claims, secret, algorithm=JWT_ALGORITHM)


def verify_access_token(token: str) -> dict[str, Any]:
    secret = _validated_signing_secret()
    if not isinstance(token, str) or not token:
        raise jwt.InvalidTokenError("Access token is required.")

    claims = jwt.decode(
        token,
        secret,
        algorithms=list(ALLOWED_JWT_ALGORITHMS),
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
        options={
            "require": [
                "sub",
                "iss",
                "aud",
                "iat",
                "exp",
                "jti",
                "token_type",
                "sid",
            ]
        },
    )
    if claims.get("token_type") != ACCESS_TOKEN_TYPE:
        raise jwt.InvalidTokenError("Token type is not valid for API access.")
    required_string_claims = ("sub", "jti", "sid")
    if any(
        not isinstance(claims.get(name), str) or not claims[name]
        for name in required_string_claims
    ):
        raise jwt.InvalidTokenError("Required access-token claims are invalid.")
    return claims
