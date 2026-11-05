from datetime import datetime, timedelta, timezone
import secrets
import unittest
from unittest.mock import patch
from uuid import uuid4

import jwt
from pydantic import SecretStr

from app.core import security
from app.core.config import settings
from app.modules.auth.models import AuthSession, PlatformRole, User
from app.modules.auth.roles import grant_registration_role


class PasswordSecurityTests(unittest.TestCase):
    def test_password_hash_uses_argon2id_and_verifies(self) -> None:
        password_hash = security.hash_password("correct horse battery staple")

        self.assertTrue(password_hash.startswith("$argon2id$"))
        self.assertTrue(
            security.verify_password("correct horse battery staple", password_hash)
        )

    def test_incorrect_password_does_not_verify(self) -> None:
        password_hash = security.hash_password("correct horse battery staple")

        self.assertFalse(
            security.verify_password("incorrect password", password_hash)
        )


class JwtSecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.secret = secrets.token_urlsafe(48)
        self.secret_patch = patch.object(settings, "jwt_secret", SecretStr(self.secret))
        self.secret_patch.start()
        self.addCleanup(self.secret_patch.stop)

    def _claims(self, **overrides: object) -> dict[str, object]:
        now = datetime.now(timezone.utc)
        claims: dict[str, object] = {
            "sub": str(uuid4()),
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
            "iat": now,
            "exp": now + timedelta(minutes=5),
            "jti": str(uuid4()),
            "token_type": "access",
            "sid": str(uuid4()),
        }
        claims.update(overrides)
        return claims

    def _signed_token(self, **claim_overrides: object) -> str:
        return jwt.encode(
            self._claims(**claim_overrides),
            security._validated_signing_secret(),
            algorithm=security.JWT_ALGORITHM,
        )

    def test_created_access_token_verifies_with_required_claims(self) -> None:
        subject = uuid4()
        session_id = uuid4()

        token = security.create_access_token(subject, session_id)
        claims = security.verify_access_token(token)

        self.assertEqual(claims["sub"], str(subject))
        self.assertEqual(claims["sid"], str(session_id))
        self.assertEqual(claims["token_type"], security.ACCESS_TOKEN_TYPE)
        self.assertTrue(claims["jti"])

    def test_expired_token_is_rejected(self) -> None:
        expired_at = datetime.now(timezone.utc) - timedelta(seconds=5)
        token = self._signed_token(exp=expired_at)

        with self.assertRaises(jwt.ExpiredSignatureError):
            security.verify_access_token(token)

    def test_wrong_signature_is_rejected(self) -> None:
        token = self._signed_token()
        wrong_secret = secrets.token_urlsafe(48)

        with patch.object(settings, "jwt_secret", SecretStr(wrong_secret)):
            with self.assertRaises(jwt.InvalidSignatureError):
                security.verify_access_token(token)

    def test_wrong_audience_is_rejected(self) -> None:
        token = self._signed_token(aud="another-service")

        with self.assertRaises(jwt.InvalidAudienceError):
            security.verify_access_token(token)

    def test_wrong_issuer_is_rejected(self) -> None:
        token = self._signed_token(iss="another-issuer")

        with self.assertRaises(jwt.InvalidIssuerError):
            security.verify_access_token(token)

    def test_unsupported_algorithm_is_rejected(self) -> None:
        token = jwt.encode(
            self._claims(), security._validated_signing_secret(), algorithm="HS384"
        )

        with self.assertRaises(jwt.InvalidAlgorithmError):
            security.verify_access_token(token)

    def test_missing_signing_secret_is_rejected(self) -> None:
        with patch.object(settings, "jwt_secret", None):
            with self.assertRaises(security.SecurityConfigurationError):
                security.create_access_token(uuid4(), uuid4())

    def test_weak_signing_secret_is_rejected(self) -> None:
        with patch.object(settings, "jwt_secret", SecretStr("x" * 48)):
            with self.assertRaises(security.SecurityConfigurationError):
                security.create_access_token(uuid4(), uuid4())

    def test_known_placeholder_signing_secret_is_rejected(self) -> None:
        with patch.object(settings, "jwt_secret", SecretStr("change-me")):
            with self.assertRaises(security.SecurityConfigurationError):
                security.create_access_token(uuid4(), uuid4())

    def test_malformed_signing_secret_is_rejected(self) -> None:
        with patch.object(settings, "jwt_secret", SecretStr("not base64!!!")):
            with self.assertRaises(security.SecurityConfigurationError):
                security.create_access_token(uuid4(), uuid4())

    def test_short_decoded_signing_secret_is_rejected(self) -> None:
        weak_secret = secrets.token_urlsafe(16)
        with patch.object(settings, "jwt_secret", SecretStr(weak_secret)):
            with self.assertRaises(security.SecurityConfigurationError):
                security.create_access_token(uuid4(), uuid4())

    def test_zero_filled_predictable_signing_secret_is_rejected(self) -> None:
        import base64

        weak_secret = base64.urlsafe_b64encode(b"\x00" * 32).decode().rstrip("=")
        with patch.object(settings, "jwt_secret", SecretStr(weak_secret)):
            with self.assertRaises(security.SecurityConfigurationError):
                security.create_access_token(uuid4(), uuid4())


class AuthModelSecurityTests(unittest.TestCase):
    def test_refresh_token_hash_is_the_only_session_credential_field(self) -> None:
        raw_token = security.generate_refresh_token()
        token_hash = security.hash_refresh_token(raw_token)
        session = AuthSession(
            user_id=uuid4(),
            token_hash=token_hash,
            family_id=uuid4(),
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        )

        self.assertEqual(len(token_hash), 64)
        self.assertNotEqual(
            token_hash,
            raw_token,
            "refresh-token hash must differ from raw token",
        )
        self.assertEqual(session.token_hash, token_hash)
        self.assertIn("token_hash", AuthSession.__table__.columns)
        self.assertNotIn("refresh_token", AuthSession.__table__.columns)

    def test_user_email_is_normalized(self) -> None:
        user = User(email="  Musician@Example.COM  ", password_hash="argon2-hash")

        self.assertEqual(user.email, "musician@example.com")

    def test_registration_role_grant_rejects_admin(self) -> None:
        user = User(email="member@example.com", password_hash="argon2-hash")
        admin_assignment_constraint = next(
            constraint
            for constraint in PlatformRole.__table__.constraints
            if constraint.name == "ck_platform_roles_admin_not_registration_assignable"
        )
        admin_role = PlatformRole(
            key="admin",
            description="Platform administrator",
            is_registration_assignable=True,
        )

        self.assertIsNotNone(admin_assignment_constraint)
        with self.assertRaises(ValueError):
            grant_registration_role(user, admin_role)

    def test_registration_role_grant_accepts_assignable_member_role(self) -> None:
        user = User(email="member@example.com", password_hash="argon2-hash")
        member_role = PlatformRole(
            key="member",
            description="Standard authenticated account",
            is_registration_assignable=True,
        )

        grant_registration_role(user, member_role)

        self.assertEqual(len(user.role_grants), 1)
        self.assertIs(user.role_grants[0].role, member_role)

    def test_registration_role_grant_rejects_arbitrary_assignable_role(self) -> None:
        user = User(email="member@example.com", password_hash="argon2-hash")
        venue_role = PlatformRole(
            key="venue",
            description="Venue role",
            is_registration_assignable=True,
        )

        with self.assertRaises(ValueError):
            grant_registration_role(user, venue_role)

        self.assertEqual(user.role_grants, [])


if __name__ == "__main__":
    unittest.main()
