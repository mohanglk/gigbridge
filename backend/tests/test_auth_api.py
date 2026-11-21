from __future__ import annotations

from datetime import datetime, timedelta, timezone
import logging
import os
import secrets
import subprocess
import sys
import unittest
from http.cookies import SimpleCookie
from unittest.mock import patch
from uuid import UUID, uuid4

import jwt
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import create_engine, select, text, update
from sqlalchemy.orm import Session, sessionmaker

from app.core import security
from app.core.config import settings
from app.core.database import get_db
from app.main import app
from app.modules.auth.models import AuthSession, User, UserPlatformRole
from app.modules.auth.rate_limit import (
    AuthRateLimiter,
    RateLimiterUnavailable,
    get_auth_rate_limiter,
)
from test_auth_database import (
    TEST_DATABASE_ENV,
    _create_test_schema_and_register_cleanup,
    _validated_test_database_url,
)
from redis_support import cleanup_test_keys, create_test_redis_client, new_test_key_prefix


class AuthenticationApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        base_url = _validated_test_database_url(os.environ.get(TEST_DATABASE_ENV))
        cls.admin_engine = create_engine(base_url)
        cls.addClassCleanup(cls.admin_engine.dispose)
        cls.schema = _create_test_schema_and_register_cleanup(cls, cls.admin_engine)

        scoped_url = base_url.update_query_dict(
            {"options": f"-csearch_path={cls.schema}"}
        )
        cls.database_url = scoped_url.render_as_string(hide_password=False)
        cls.engine = create_engine(scoped_url)
        cls.addClassCleanup(cls.engine.dispose)
        cls.session_factory = sessionmaker(
            bind=cls.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )
        cls.backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        cls._run_migration("head")

        def override_get_db():
            with cls.session_factory() as db:
                yield db

        previous_override = app.dependency_overrides.get(get_db)
        app.dependency_overrides[get_db] = override_get_db

        def restore_dependency_override() -> None:
            if previous_override is None:
                app.dependency_overrides.pop(get_db, None)
            else:
                app.dependency_overrides[get_db] = previous_override

        cls.addClassCleanup(restore_dependency_override)
        cls.client = TestClient(app)
        cls.addClassCleanup(cls.client.close)

        cls.jwt_secret_patch = patch.object(
            settings, "jwt_secret", SecretStr(secrets.token_urlsafe(48))
        )
        cls.jwt_secret_patch.start()
        cls.addClassCleanup(cls.jwt_secret_patch.stop)
        cls.environment_patch = patch.object(settings, "app_environment", "production")
        cls.environment_patch.start()
        cls.addClassCleanup(cls.environment_patch.stop)
        cls.rate_limit_secret_patch = patch.object(
            settings,
            "auth_rate_limit_hmac_secret",
            SecretStr(secrets.token_urlsafe(48)),
        )
        cls.rate_limit_secret_patch.start()
        cls.addClassCleanup(cls.rate_limit_secret_patch.stop)

    @classmethod
    def _run_migration(cls, revision: str) -> None:
        environment = os.environ.copy()
        environment["DATABASE_URL"] = cls.database_url
        subprocess.run(
            [sys.executable, "-m", "alembic", "-c", "alembic.ini", "upgrade", revision],
            cwd=cls.backend_dir,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
        )

    def setUp(self) -> None:
        self.email = f"{uuid4().hex}@example.com"
        self.password = "correct horse battery staple"
        self.redis = create_test_redis_client()
        self.redis.ping()
        self.addCleanup(self.redis.close)
        self.rate_limit_prefix = new_test_key_prefix()
        self.addCleanup(
            cleanup_test_keys, self.redis, self.rate_limit_prefix
        )
        self.rate_limiter = AuthRateLimiter(self.redis, self.rate_limit_prefix)
        previous_limiter = app.dependency_overrides.get(get_auth_rate_limiter)
        app.dependency_overrides[get_auth_rate_limiter] = lambda: self.rate_limiter

        def restore_rate_limiter() -> None:
            if previous_limiter is None:
                app.dependency_overrides.pop(get_auth_rate_limiter, None)
            else:
                app.dependency_overrides[get_auth_rate_limiter] = previous_limiter

        self.addCleanup(restore_rate_limiter)

    def register(self, email: str | None = None, password: str | None = None):
        return self.client.post(
            "/api/v1/auth/register",
            json={"email": email or self.email, "password": password or self.password},
        )

    def create_account(self) -> str:
        response = self.register()
        self.assertEqual(response.status_code, 202, response.text)
        with Session(self.engine) as db:
            user = db.scalar(select(User).where(User.email == self.email))
            self.assertIsNotNone(user)
            return str(user.id)

    def login(self, email: str | None = None, password: str | None = None):
        return self.client.post(
            "/api/v1/auth/login",
            json={"email": email or self.email, "password": password or self.password},
        )

    def session_for(self, user_id: UUID) -> AuthSession:
        with Session(self.engine) as db:
            return db.scalar(select(AuthSession).where(AuthSession.user_id == user_id))

    def assert_safe_user_payload(self, payload: dict) -> None:
        forbidden = {"password", "password_hash", "refresh_token", "token_hash"}
        self.assertTrue(forbidden.isdisjoint(payload))

    def test_successful_registration_normalizes_email_and_hashes_password(self) -> None:
        response = self.register(email=f"  {self.email.upper()}  ")

        self.assertEqual(response.status_code, 202, response.text)
        self.assertEqual(response.json(), {"message": "Request accepted."})
        self.assert_safe_user_payload(response.json())
        with Session(self.engine) as db:
            user = db.scalar(select(User).where(User.email == self.email))
            self.assertIsNotNone(user)
            self.assertTrue(user.password_hash.startswith("$argon2id$"))
            self.assertTrue(security.verify_password(self.password, user.password_hash))
            grants = db.scalars(
                select(UserPlatformRole).where(UserPlatformRole.user_id == user.id)
            ).all()
            self.assertEqual([grant.role_key for grant in grants], ["member"])

    def test_duplicate_email_is_rejected_without_sensitive_response(self) -> None:
        original_response = self.register()
        with Session(self.engine) as db:
            original_user = db.scalar(select(User).where(User.email == self.email))
            original_hash = original_user.password_hash
        duplicate_response = self.register(
            email=self.email.upper(), password="a different password"
        )

        self.assertEqual(original_response.status_code, 202)
        self.assertEqual(duplicate_response.status_code, original_response.status_code)
        self.assertEqual(duplicate_response.json(), original_response.json())
        self.assertEqual(duplicate_response.json(), {"message": "Request accepted."})
        with Session(self.engine) as db:
            users = db.scalars(select(User).where(User.email == self.email)).all()
            self.assertEqual(len(users), 1)
            self.assertEqual(users[0].password_hash, original_hash)

    def test_registration_rejects_admin_and_arbitrary_roles(self) -> None:
        for role_data in ({"role": "admin"}, {"roles": ["member", "admin"]}):
            response = self.client.post(
                "/api/v1/auth/register",
                json={"email": f"{uuid4().hex}@example.com", "password": self.password, **role_data},
            )
            self.assertEqual(response.status_code, 422)

    def test_successful_login_creates_session_and_http_only_refresh_cookie(self) -> None:
        user_id = UUID(self.create_account())
        response = self.login()

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["token_type"], "bearer")
        self.assertEqual(body["user"]["id"], str(user_id))
        self.assert_safe_user_payload(body["user"])
        self.assertNotIn("refresh_token", body)
        self.assertNotIn("token_hash", body)
        self.assertEqual(response.headers["cache-control"], "no-store")

        cookie = SimpleCookie()
        cookie.load(response.headers["set-cookie"])
        refresh_cookie = cookie["gigbridge_refresh"]
        self.assertTrue(refresh_cookie["httponly"])
        self.assertTrue(refresh_cookie["secure"])
        self.assertEqual(refresh_cookie["samesite"], "lax")
        self.assertEqual(refresh_cookie["path"], "/api/v1/auth/refresh")

        raw_refresh_token = response.cookies.get("gigbridge_refresh")
        self.assertTrue(raw_refresh_token)
        auth_session = self.session_for(user_id)
        self.assertEqual(
            auth_session.token_hash,
            security.hash_refresh_token(raw_refresh_token),
        )
        self.assertNotEqual(auth_session.token_hash, raw_refresh_token)
        claims = security.verify_access_token(body["access_token"])
        self.assertEqual(claims["sid"], str(auth_session.id))

    def test_incorrect_credentials_have_generic_response(self) -> None:
        self.create_account()
        wrong_password = self.login(password="incorrect password")
        unknown_email = self.login(email=f"{uuid4().hex}@example.com")

        self.assertEqual(wrong_password.status_code, 401)
        self.assertEqual(wrong_password.json(), unknown_email.json())
        self.assertEqual(wrong_password.json()["detail"], "Invalid email or password.")

    def test_disabled_account_is_rejected_with_generic_credentials_error(self) -> None:
        user_id = UUID(self.create_account())
        with Session(self.engine) as db:
            db.execute(update(User).where(User.id == user_id).values(is_active=False))
            db.commit()

        response = self.login()

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Invalid email or password.")
        self.assertNotIn("set-cookie", response.headers)

    def test_me_returns_safe_current_user(self) -> None:
        self.create_account()
        login_response = self.login()
        response = self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {login_response.json()['access_token']}"},
        )

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["email"], self.email)
        self.assert_safe_user_payload(response.json())

    def test_me_rejects_missing_and_invalid_bearer_tokens(self) -> None:
        missing = self.client.get("/api/v1/auth/me")
        invalid = self.client.get(
            "/api/v1/auth/me", headers={"Authorization": "Bearer invalid-token"}
        )

        self.assertEqual(missing.status_code, 401)
        self.assertEqual(invalid.status_code, 401)
        self.assertEqual(missing.headers["www-authenticate"], "Bearer")

    def test_me_rejects_expired_access_token(self) -> None:
        user_id = uuid4()
        now = datetime.now(timezone.utc)
        token = jwt.encode(
            {
                "sub": str(user_id),
                "sid": str(uuid4()),
                "iss": settings.jwt_issuer,
                "aud": settings.jwt_audience,
                "iat": now - timedelta(minutes=2),
                "exp": now - timedelta(minutes=1),
                "jti": str(uuid4()),
                "token_type": "access",
            },
            security._validated_signing_secret(),
            algorithm="HS256",
        )
        response = self.client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
        )

        self.assertEqual(response.status_code, 401)

    def test_me_rejects_revoked_session(self) -> None:
        user_id = UUID(self.create_account())
        login_response = self.login()
        token = login_response.json()["access_token"]
        auth_session = self.session_for(user_id)
        with Session(self.engine) as db:
            db.execute(
                update(AuthSession)
                .where(AuthSession.id == auth_session.id)
                .values(revoked_at=datetime.now(timezone.utc))
            )
            db.commit()

        response = self.client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
        )

        self.assertEqual(response.status_code, 401)

    def test_me_rejects_inactive_user(self) -> None:
        user_id = UUID(self.create_account())
        login_response = self.login()
        with Session(self.engine) as db:
            db.execute(update(User).where(User.id == user_id).values(is_active=False))
            db.commit()

        response = self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {login_response.json()['access_token']}"},
        )

        self.assertEqual(response.status_code, 401)

    def test_me_rejects_a_session_owned_by_another_user(self) -> None:
        first_user_id = UUID(self.create_account())
        self.login()

        second_email = f"{uuid4().hex}@example.com"
        second_registration = self.register(email=second_email)
        self.assertEqual(second_registration.status_code, 202)
        with Session(self.engine) as db:
            second_user = db.scalar(select(User).where(User.email == second_email))
            self.assertIsNotNone(second_user)
            second_user_id = second_user.id
        self.login(email=second_email)

        mismatched_session_token = security.create_access_token(
            first_user_id, self.session_for(second_user_id).id
        )

        response = self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {mismatched_session_token}"},
        )

        self.assertEqual(response.status_code, 401)

    def test_me_rejects_expired_database_session(self) -> None:
        user_id = UUID(self.create_account())
        login_response = self.login()
        auth_session = self.session_for(user_id)
        with Session(self.engine) as db:
            db.execute(
                update(AuthSession)
                .where(AuthSession.id == auth_session.id)
                .values(expires_at=datetime.now(timezone.utc) - timedelta(seconds=1))
            )
            db.commit()

        response = self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {login_response.json()['access_token']}"},
        )

        self.assertEqual(response.status_code, 401)

    def test_cookie_max_age_matches_refresh_session_expiry(self) -> None:
        user_id = UUID(self.create_account())
        response = self.login()
        cookie = SimpleCookie()
        cookie.load(response.headers["set-cookie"])
        cookie_max_age = int(cookie["gigbridge_refresh"]["max-age"])
        auth_session = self.session_for(user_id)

        self.assertEqual(
            cookie_max_age,
            settings.refresh_token_expire_days * 24 * 60 * 60,
        )
        self.assertLessEqual(
            abs(
                (auth_session.expires_at - auth_session.issued_at).total_seconds()
                - cookie_max_age
            ),
            2,
        )

    def test_registration_ip_rate_limit_returns_retry_after(self) -> None:
        with (
            patch.object(settings, "auth_register_ip_limit", 1),
            patch.object(settings, "auth_register_account_limit", 10),
        ):
            first = self.register()
            second = self.register(email=f"{uuid4().hex}@example.com")

        self.assertEqual(first.status_code, 202)
        self.assertEqual(second.status_code, 429)
        self.assertGreaterEqual(int(second.headers["retry-after"]), 1)
        self.assertEqual(
            second.json(),
            {"detail": "Too many authentication attempts. Please try again later."},
        )

    def test_login_rate_limit_uses_generic_response(self) -> None:
        with (
            patch.object(settings, "auth_login_ip_limit", 1),
            patch.object(settings, "auth_login_account_limit", 10),
        ):
            first = self.login(email=f"{uuid4().hex}@example.com")
            second = self.login(email=f"{uuid4().hex}@example.com")

        self.assertEqual(first.status_code, 401)
        self.assertEqual(second.status_code, 429)
        self.assertGreaterEqual(int(second.headers["retry-after"]), 1)
        self.assertNotIn("email", second.json()["detail"].lower())

    def test_redis_unavailable_returns_controlled_503(self) -> None:
        class UnavailableLimiter:
            def enforce(self, *_args, **_kwargs):
                raise RateLimiterUnavailable("offline")

        previous_limiter = app.dependency_overrides.get(get_auth_rate_limiter)
        app.dependency_overrides[get_auth_rate_limiter] = lambda: UnavailableLimiter()
        try:
            response = self.register()
        finally:
            if previous_limiter is None:
                app.dependency_overrides.pop(get_auth_rate_limiter, None)
            else:
                app.dependency_overrides[get_auth_rate_limiter] = previous_limiter

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.headers["retry-after"], "1")
        self.assertNotIn(self.email, response.text)

    def test_passwords_and_tokens_do_not_appear_in_application_logs(self) -> None:
        class CaptureLogs(logging.Handler):
            def __init__(self) -> None:
                super().__init__()
                self.messages: list[str] = []

            def emit(self, record: logging.LogRecord) -> None:
                self.messages.append(record.getMessage())

        handler = CaptureLogs()
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        try:
            registration = self.register()
            login_response = self.login()
            access_token = login_response.json()["access_token"]
            refresh_token = login_response.cookies.get("gigbridge_refresh")
            me = self.client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        finally:
            root_logger.removeHandler(handler)

        self.assertEqual(registration.status_code, 202)
        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(me.status_code, 200)
        captured = "\n".join(handler.messages)
        for sensitive_value in (self.password, access_token, refresh_token):
            self.assertNotIn(sensitive_value, captured)


if __name__ == "__main__":
    unittest.main()
