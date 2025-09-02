# Security Model (Phase 2)

## Identity & AuthN
- JWT issued by `/auth/login`.
- Token includes user and tenant claims.
- Send as `Authorization: Bearer <token>`.

## Tenancy
- Tenant selected via `Host` header (e.g., `tenant1.lvh.me`).
- All reads/writes scoped per tenant (prefix collections or pass tenant to repo methods).

## RBAC
- Roles: `owner` (admin endpoints), `analyst` (read-only analytics), others as added.
- Enforced on every non-public route.

## Rate Limiting
- Target: `/kavach/scan/start` → 5/min.  
- In tests may be disabled; production should enforce 429.

## Data Storage
- Mongo indexes per tenant/module (not shown here, but defined in repo/db manager).
- For tests, in-memory repos avoid real infra.

## Transport & Secrets
- Use HTTPS in prod.
- Secret management via env vars / vault.
