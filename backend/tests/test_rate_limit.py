from __future__ import annotations

import secrets
import os
import unittest
from unittest.mock import patch

from fastapi import HTTPException
from starlette.requests import Request
from pydantic import SecretStr, ValidationError
from redis.exceptions import ConnectionError as RedisConnectionError

from app.core.config import Settings, settings
from app.modules.auth.rate_limit import (
    AuthRateLimiter,
    RateLimitExceeded,
    RateLimiterUnavailable,
    enforce_auth_rate_limit,
    resolve_client_ip,
)
from redis_support import (
    TEST_REDIS_URL_ENV,
    cleanup_test_keys,
    create_test_redis_client,
    new_test_key_prefix,
    validate_test_redis_url,
)


def make_request(peer: str, forwarded_for: str | None = None) -> Request:
    headers = []
    if forwarded_for is not None:
        headers.append((b"x-forwarded-for", forwarded_for.encode("ascii")))
    return Request(
        {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "POST",
            "scheme": "http",
            "path": "/",
            "raw_path": b"/",
            "query_string": b"",
            "headers": headers,
            "client": (peer, 12345),
            "server": ("testserver", 80),
        }
    )


class RedisRateLimitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.redis = create_test_redis_client()
        self.redis.ping()
        self.addCleanup(self.redis.close)
        self.key_prefix = new_test_key_prefix()
        self.addCleanup(cleanup_test_keys, self.redis, self.key_prefix)
        self.key_patch = patch.object(
            settings,
            "auth_rate_limit_hmac_secret",
            SecretStr(secrets.token_urlsafe(48)),
        )
        self.key_patch.start()
        self.addCleanup(self.key_patch.stop)
        self.limiter = AuthRateLimiter(self.redis, self.key_prefix)

    def test_test_redis_configuration_is_explicit_and_isolated(self) -> None:
        self.assertEqual(
            validate_test_redis_url("redis://localhost:6379/15"),
            "redis://localhost:6379/15",
        )
        with self.assertRaises(RuntimeError):
            validate_test_redis_url("redis://localhost:6379/0")

        with patch.dict(os.environ, {"REDIS_URL": "redis://localhost:6379/0"}):
            os.environ.pop(TEST_REDIS_URL_ENV, None)
            with self.assertRaises(RuntimeError):
                create_test_redis_client()

    def test_requests_below_configured_limits_are_allowed(self) -> None:
        with (
            patch.object(settings, "auth_login_ip_limit", 3),
            patch.object(settings, "auth_login_account_limit", 3),
            patch.object(settings, "auth_login_ip_window_seconds", 60),
            patch.object(settings, "auth_login_account_window_seconds", 60),
        ):
            self.limiter.enforce("login", "192.0.2.10", "member@example.com")
            self.limiter.enforce("login", "192.0.2.10", "member@example.com")

    def test_registration_ip_limit_and_retry_after(self) -> None:
        with (
            patch.object(settings, "auth_register_ip_limit", 1),
            patch.object(settings, "auth_register_account_limit", 10),
            patch.object(settings, "auth_register_ip_window_seconds", 60),
            patch.object(settings, "auth_register_account_window_seconds", 60),
        ):
            self.limiter.enforce("register", "192.0.2.11", "one@example.com")
            request = make_request("192.0.2.11")
            with self.assertRaises(HTTPException) as error:
                enforce_auth_rate_limit(
                    self.limiter, "register", request, "two@example.com"
                )

        self.assertEqual(error.exception.status_code, 429)
        self.assertGreaterEqual(int(error.exception.headers["Retry-After"]), 1)
        self.assertEqual(
            error.exception.detail,
            "Too many authentication attempts. Please try again later.",
        )

    def test_login_account_limit_is_separate_from_ip_limit(self) -> None:
        with (
            patch.object(settings, "auth_login_ip_limit", 10),
            patch.object(settings, "auth_login_account_limit", 1),
            patch.object(settings, "auth_login_ip_window_seconds", 60),
            patch.object(settings, "auth_login_account_window_seconds", 60),
            patch.object(settings, "auth_register_ip_limit", 1),
            patch.object(settings, "auth_register_account_limit", 1),
            patch.object(settings, "auth_register_ip_window_seconds", 60),
            patch.object(settings, "auth_register_account_window_seconds", 60),
        ):
            self.limiter.enforce("login", "192.0.2.12", "member@example.com")
            with self.assertRaises(RateLimitExceeded):
                self.limiter.enforce("login", "192.0.2.13", "MEMBER@example.com")
            # The login bucket does not consume the separate registration limit.
            self.limiter.enforce("register", "192.0.2.12", "member@example.com")

    def test_account_identifiers_are_hashed_in_redis_keys(self) -> None:
        email = "sensitive.person@example.com"
        ip_key, account_key = self.limiter.bucket_keys("login", "192.0.2.14", email)

        self.assertNotIn(email, ip_key)
        self.assertNotIn(email, account_key)
        self.assertIn(":account:", account_key)

    def test_redis_connection_failure_becomes_controlled_503(self) -> None:
        class FailingRedis:
            def eval(self, *_args, **_kwargs):
                raise RedisConnectionError("test redis unavailable")

        limiter = AuthRateLimiter(FailingRedis(), self.key_prefix)
        request = make_request("192.0.2.15")
        with self.assertRaises(HTTPException) as error:
            enforce_auth_rate_limit(limiter, "login", request, "member@example.com")

        self.assertEqual(error.exception.status_code, 503)
        self.assertEqual(error.exception.headers["Retry-After"], "1")
        self.assertNotIn("member@example.com", error.exception.detail)

    def test_untrusted_forwarded_ip_is_ignored(self) -> None:
        with patch.object(settings, "trusted_proxy_ips", ["10.10.0.0/16"]):
            resolved = resolve_client_ip(
                make_request("198.51.100.20", "203.0.113.99")
            )

        self.assertEqual(resolved, "198.51.100.20")

    def test_trusted_proxy_chain_resolves_nearest_untrusted_client(self) -> None:
        with patch.object(settings, "trusted_proxy_ips", ["10.10.0.0/16"]):
            resolved = resolve_client_ip(
                make_request("10.10.0.3", "198.51.100.7, 10.10.0.2")
            )

        self.assertEqual(resolved, "198.51.100.7")

    def test_production_requires_explicit_https_cors_origins(self) -> None:
        with self.assertRaises(ValidationError):
            Settings(app_environment="production")
        with self.assertRaises(ValidationError):
            Settings(cors_allowed_origins=["*"])

        production_settings = Settings(
            app_environment="production",
            cors_allowed_origins=["https://app.gigbridge.example"],
        )
        self.assertTrue(production_settings.secure_auth_cookies)

    def test_unsafe_cookie_samesite_value_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            Settings(
                app_environment="production",
                cors_allowed_origins=["https://app.gigbridge.example"],
                auth_cookie_samesite="none",
            )


if __name__ == "__main__":
    unittest.main()
