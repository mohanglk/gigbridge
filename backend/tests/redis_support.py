"""Helpers for an isolated logical Redis database used only by tests."""

from urllib.parse import urlsplit
from uuid import uuid4

from redis import Redis

TEST_REDIS_DATABASE = "15"
TEST_REDIS_URL_ENV = "GIGBRIDGE_TEST_REDIS_URL"
TEST_KEY_PREFIX = "gigbridge:test:auth-rate-limit"


def validate_test_redis_url(redis_url: str | None) -> str:
    if not redis_url:
        raise RuntimeError(f"Set {TEST_REDIS_URL_ENV} to the dedicated Redis test database.")
    parsed = urlsplit(redis_url)
    if parsed.scheme not in {"redis", "rediss"} or parsed.path.lstrip("/") != TEST_REDIS_DATABASE:
        raise RuntimeError(
            f"Refusing Redis integration tests: use a Redis URL with database {TEST_REDIS_DATABASE}."
        )
    return redis_url


def create_test_redis_client(redis_url: str | None = None) -> Redis:
    import os

    configured_url = redis_url if redis_url is not None else os.environ.get(TEST_REDIS_URL_ENV)
    return Redis.from_url(
        validate_test_redis_url(configured_url),
        socket_connect_timeout=1,
        socket_timeout=1,
    )


def new_test_key_prefix() -> str:
    return f"{TEST_KEY_PREFIX}:{uuid4().hex}"


def cleanup_test_keys(client: Redis, key_prefix: str) -> None:
    """Remove only keys under this run's unique test prefix; never FLUSH a DB."""
    if not key_prefix.startswith(f"{TEST_KEY_PREFIX}:"):
        raise RuntimeError("Refusing to clean keys outside the authentication test namespace.")
    keys = list(client.scan_iter(match=f"{key_prefix}:*", count=100))
    if keys:
        client.unlink(*keys)
