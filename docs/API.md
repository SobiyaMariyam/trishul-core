# Trishul API (Phase 2)

Base URL: `{{base_url}}` (default `http://127.0.0.1:8000`)  
Tenant header: `Host: {{host}}` (example `tenant1.lvh.me`)  
Auth: `Authorization: Bearer <JWT>`

## Auth
### POST /auth/login
Request: `{ "username": "owner", "password": "owner" }`  
Response: `{ "token": "<jwt>" }`

## Kavach
### POST /kavach/scan/start
Starts a mock scan. Returns 200/202.

### GET /kavach/scan/history
Returns `[{ id, status, started_at, ... }]`.

## Rudra (Cloud)
### POST /rudra/cloud/mock-usage
Body: `{ "usage": [20,25,30,33,31] }` → stores mock usage for tenant.

### GET /rudra/cloud/forecast
Returns `[numbers...]` or `{ "forecast": [...] }`. All values non-negative.

### GET /rudra/cloud/configcheck
Sanity/config info for the module.

## Trinetra (QC)
### POST /trinetra/qc/upload (multipart/form-data)
Key: `image` (file). Returns 200 on mock store.

### GET /trinetra/qc/results
Returns `[{ id, file_name, verdict, score, ts }, ...]`
(or `{ "results": [...] }` in some builds).

## Admin
### GET /admin/stats
RBAC-protected; returns counters per tenant/module.

### GET /admin/health
Always 200 with `{ ok: true }`.

## Nandi (Email)
### POST /nandi/send
Body: `{ "to": "...", "subject": "...", "body": "..." }`.  
Creates a mock `email_logs` entry.
