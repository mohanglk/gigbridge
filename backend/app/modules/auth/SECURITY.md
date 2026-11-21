# Authentication foundation security requirements

## HS256 signing key

Set `JWT_SECRET` to unpadded URL-safe Base64 representing at least 32 bytes
(256 bits) of cryptographically generated key material. Generate a key with:

```sh
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Runtime format and size checks cannot prove how a value was generated or its
entropy. Operators must use a cryptographic random generator, keep the value in
an environment secret store, and never commit it. Do not use example values,
passwords, phrases, or other predictable strings.

## Role assignment

Public registration may grant only the fixed `member` role. It must not accept a
role key or role list from an API request. Platform administrator grants require
a trusted administrative workflow with explicit authorization and audit logging;
they are not public registration operations. Organization membership permissions
remain separate from platform-level roles.

## Mandatory Task 3.2 refresh-token requirements

Refresh endpoints must rotate tokens atomically in one database transaction.
Concurrent requests presenting the same refresh token must result in at most one
successful rotation; use row locking or an equivalent conditional state change.
Persist only token hashes. If a revoked or already-replaced token is presented,
revoke all active sessions in its token family and require a fresh authentication
grant. Expiration and revocation must be checked before issuing replacement
tokens. These requirements are mandatory before refresh endpoints are released.

## Client token transport

The web login endpoint returns its short-lived access token in the response and
sets the opaque refresh token only in an HttpOnly cookie scoped to the future
refresh route. The cookie uses `SameSite=Lax` and is `Secure` when
`APP_ENVIRONMENT=production`. Web clients should keep access tokens in memory,
not persistent browser storage. `CORS_ALLOWED_ORIGINS` must list the trusted web
origins when deploying the API with credentialed browser requests.

Native Android and iOS refresh-token transport remains a Task 3.2 design
decision. Before enabling it, specify a native-client response/transport contract
and platform secure-storage guidance for Keychain or Android Keystore. Do not
expose the refresh token through browser JSON or use localStorage as a workaround.

## Authentication rate limits

Authentication routes use atomic Redis counters for both source IP and normalized
account identifier. Email identifiers are HMAC-SHA-256 values in Redis keys; the
raw address is not stored there. Configure `AUTH_RATE_LIMIT_HMAC_SECRET` as an
independent random key using `secrets.token_urlsafe(32)`. Keep it in an environment
secret store. Redis errors fail closed with HTTP 503; the application does not
bypass production limits when Redis is unavailable.

The documented starter limits are configurable through these settings:

| Operation | Bucket | Default limit | Window |
|---|---|---:|---:|
| Registration | IP | 10 | 3600 seconds |
| Registration | Account | 3 | 3600 seconds |
| Login | IP | 20 | 900 seconds |
| Login | Account | 10 | 900 seconds |

These are initial values, not universal production thresholds. Tune them for
expected traffic, abuse patterns, and operational capacity. `TRUSTED_PROXY_IPS`
must contain only the actual proxy addresses/CIDRs that sanitize and append
`X-Forwarded-For`; forwarded headers from every other peer are ignored.

## Mandatory Task 3.2.2 CSRF requirements

Before adding the cookie-authenticated refresh endpoint, validate the request
`Origin` (and `Referer` where needed) against the configured HTTPS web origins and
require a CSRF token or an equivalently strong request-binding control. Keep
SameSite and CORS as defense in depth; neither replaces CSRF validation. Reject
cross-origin refresh requests before rotating or issuing credentials.
