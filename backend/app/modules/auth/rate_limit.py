"""Atomic Redis rate limits for public authentication requests."""

from dataclasses import dataclass
import base64
import binascii
import hashlib
import hmac
import ipaddress
from functools import lru_cache

from fastapi import HTTPException, Request
from redis import Redis
from redis.exceptions import RedisError
from sqlalchemy.engine import URL

from app.core.config import settings

_CONSUME_SCRIPT = """
local blocked = 0
local retry_after = 0
for index, key in ipairs(KEYS) do
    local limit = tonumber(ARGV[(index - 1) * 2 + 1])
    local window_ms = tonumber(ARGV[(index - 1) * 2 + 2])
    local count = redis.call('INCR', key)
    local ttl = redis.call('PTTL', key)
    if ttl < 0 then
        redis.call('PEXPIRE', key, window_ms)
        ttl = window_ms
    end
    if count > limit then
        blocked = 1
        local seconds = math.ceil(ttl / 1000)
        if seconds > retry_after then
            retry_after = seconds
        end
    end
end
return {blocked, retry_after}
"""

DEFAULT_KEY_PREFIX = "gigbridge:auth-rate-limit:v1"


class RateLimiterUnavailable(Exception):
    """Raised when rate limiting cannot be safely evaluated."""


class RateLimitExceeded(Exception):
    def __init__(self, retry_after: int) -> None:
        self.retry_after = max(1, retry_after)
        super().__init__("Authentication request rate limit exceeded.")


@dataclass(frozen=True)
class RateLimitPolicy:
    ip_limit: int
    ip_window_seconds: int
    account_limit: int
    account_window_seconds: int


def policy_for(operation: str) -> RateLimitPolicy:
    if operation == "register":
        return RateLimitPolicy(
            settings.auth_register_ip_limit,
            settings.auth_register_ip_window_seconds,
            settings.auth_register_account_limit,
            settings.auth_register_account_window_seconds,
        )
    if operation == "login":
        return RateLimitPolicy(
            settings.auth_login_ip_limit,
            settings.auth_login_ip_window_seconds,
            settings.auth_login_account_limit,
            settings.auth_login_account_window_seconds,
        )
    raise ValueError("Unsupported authentication rate-limit operation.")


def _validated_hmac_key() -> bytes:
    configured = settings.auth_rate_limit_hmac_secret
    if configured is None:
        raise RateLimiterUnavailable("Rate-limit identifier key is not configured.")

    secret = configured.get_secret_value()
    if not secret or secret != secret.strip():
        raise RateLimiterUnavailable("Rate-limit identifier key is malformed.")
    try:
        key = base64.b64decode(
            secret + "=" * (-len(secret) % 4), altchars=b"-_", validate=True
        )
    except (binascii.Error, ValueError) as exc:
        raise RateLimiterUnavailable("Rate-limit identifier key is malformed.") from exc

    if (
        base64.urlsafe_b64encode(key).decode("ascii").rstrip("=") != secret
        or len(key) < 32
        or len(set(key)) == 1
    ):
        raise RateLimiterUnavailable("Rate-limit identifier key is too weak or malformed.")
    return key


def _identifier_digest(key: bytes, kind: str, value: str) -> str:
    normalized = value.strip().lower() if kind == "account" else value
    message = f"gigbridge-auth-rate-limit-v1\0{kind}\0{normalized}".encode("utf-8")
    return hmac.new(key, message, hashlib.sha256).hexdigest()


class AuthRateLimiter:
    def __init__(self, redis_client: Redis, key_prefix: str = DEFAULT_KEY_PREFIX) -> None:
        self.redis = redis_client
        self.key_prefix = key_prefix.rstrip(":")

    def bucket_keys(self, operation: str, client_ip: str, email: str) -> tuple[str, str]:
        key = _validated_hmac_key()
        ip_hash = _identifier_digest(key, "ip", client_ip)
        account_hash = _identifier_digest(key, "account", email)
        return (
            f"{self.key_prefix}:{operation}:ip:{ip_hash}",
            f"{self.key_prefix}:{operation}:account:{account_hash}",
        )

    def enforce(self, operation: str, client_ip: str, email: str) -> None:
        policy = policy_for(operation)
        keys = self.bucket_keys(operation, client_ip, email)
        try:
            blocked, retry_after = self.redis.eval(
                _CONSUME_SCRIPT,
                2,
                *keys,
                policy.ip_limit,
                policy.ip_window_seconds * 1000,
                policy.account_limit,
                policy.account_window_seconds * 1000,
            )
        except RedisError as exc:
            raise RateLimiterUnavailable("Rate-limit storage is unavailable.") from exc

        if int(blocked):
            raise RateLimitExceeded(int(retry_after))


def resolve_client_ip(request: Request) -> str:
    """Trust forwarded hops only when the direct peer is a configured proxy."""
    peer = request.client.host if request.client is not None else None
    if not peer:
        raise RateLimiterUnavailable("Client address is unavailable.")

    try:
        peer_ip = ipaddress.ip_address(peer)
    except ValueError:
        # Test clients and non-IP ASGI transports still have a server-supplied
        # peer identity; never use forwarding headers for these transports.
        return peer

    try:
        trusted_networks = [
            ipaddress.ip_network(proxy, strict=False)
            for proxy in settings.trusted_proxy_ips
        ]
    except ValueError as exc:
        raise RateLimiterUnavailable("Trusted proxy configuration is invalid.") from exc

    if not any(peer_ip in network for network in trusted_networks):
        return peer_ip.compressed

    forwarded_header = request.headers.get("x-forwarded-for")
    if not forwarded_header:
        return peer_ip.compressed

    try:
        forwarded_ips = [
            ipaddress.ip_address(part.strip())
            for part in forwarded_header.split(",")
        ]
    except ValueError:
        # A malformed chain cannot be used to select an attacker-controlled IP.
        return peer_ip.compressed

    current = peer_ip
    for hop in reversed(forwarded_ips):
        if not any(current in network for network in trusted_networks):
            break
        current = hop
    return current.compressed


def enforce_auth_rate_limit(
    limiter: AuthRateLimiter,
    operation: str,
    request: Request,
    email: str,
) -> None:
    try:
        limiter.enforce(operation, resolve_client_ip(request), email)
    except RateLimitExceeded as exc:
        raise HTTPException(
            status_code=429,
            detail="Too many authentication attempts. Please try again later.",
            headers={"Retry-After": str(exc.retry_after)},
        ) from None
    except RateLimiterUnavailable:
        # Fail closed in every environment; in production this prevents an
        # outage from silently disabling authentication abuse controls.
        raise HTTPException(
            status_code=503,
            detail="Authentication service is temporarily unavailable.",
            headers={"Retry-After": "1"},
        ) from None


@lru_cache(maxsize=1)
def get_auth_rate_limiter() -> AuthRateLimiter:
    redis_url = settings.redis_url
    if isinstance(redis_url, URL):
        redis_url = redis_url.render_as_string(hide_password=False)
    client = Redis.from_url(
        redis_url,
        socket_connect_timeout=1,
        socket_timeout=1,
        health_check_interval=30,
    )
    return AuthRateLimiter(client)
