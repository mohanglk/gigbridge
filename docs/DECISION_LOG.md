# GigBridge Decision Log

## Authentication API decisions

### Registration responses

Registration returns the same generic status and response body for newly
registered and already-existing email addresses. Duplicate protection remains
enforced by the database uniqueness constraint, including concurrent
registration attempts.

### Registration and login rate limits

Registration and login use separate configurable limits for source IP and
account identifier. The Redis operation checks and increments its buckets
atomically. Redis unavailability returns a controlled HTTP 503; the API does
not bypass rate limiting when Redis is unavailable.

Email account identifiers and IP values used in rate-limit keys are
HMAC-hashed. Raw account identifiers and IP values are not included in those
keys. Forwarded IP values are trusted only when the direct peer belongs to the
configured trusted-proxy list; arbitrary `X-Forwarded-For` headers are ignored.

### Production browser security

Production requires explicit HTTPS CORS origins and Secure authentication
cookies. Wildcard CORS origins are rejected. Credentialed CORS must use the
configured explicit origins.

### Deferred authentication work

Refresh-token rotation, replay detection and family revocation, single-session
logout, and logout-all remain future implementation tasks. Before a
cookie-authenticated refresh endpoint is introduced, it must validate Origin
(and Referer where applicable) and use a CSRF token or an equivalent
request-binding control. SameSite and CORS are defense in depth and do not
replace CSRF protection.

Native-mobile refresh-token transport remains a future design decision. The
contract must avoid browser-only assumptions and specify secure storage using
platform facilities such as iOS Keychain and Android Keystore. No refresh-token
or logout flow is implemented by this decision log.

## Phase 0 verification gate

A fresh successful CI run is required before PR approval and merge. The
previously reported 57 passing tests could not be rerun during final
verification; fresh CI results remain pending.
