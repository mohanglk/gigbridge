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
