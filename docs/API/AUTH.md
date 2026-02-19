# NADAKKI AI Suite - Authentication Guide

## Overview

NADAKKI uses a header-based authentication model with two layers:

1. **Tenant identification** via `X-Tenant-ID`
2. **Admin authentication** via `X-Admin-Key`

---

## Tenant Identification

All requests should include the `X-Tenant-ID` header with the tenant slug.

```
X-Tenant-ID: credicefi
```

If omitted, defaults to `credicefi`.

The tenant ID is used for:
- Row Level Security (RLS) — queries only return data for the tenant
- Usage tracking — executions are counted per tenant
- Rate limiting — 100 requests/min per tenant
- Audit logging — all requests are logged with tenant context

---

## Admin Authentication

Administrative endpoints require the `X-Admin-Key` header.

```
X-Admin-Key: nadakki_admin_2025_master
```

### Admin Roles

| Key | Role | Scope |
|-----|------|-------|
| `nadakki_admin_2025_master` | super_admin | All tenants |
| `nadakki_admin_credicefi_2025` | tenant_admin | credicefi only |

### Protected Endpoints

- `POST /api/v1/tenants/onboard`
- `PATCH /api/v1/tenants/{slug}/config`
- `POST /api/v1/gates/{gate_id}/approve`
- `POST /api/v1/gates/{gate_id}/reject`
- `POST /api/v1/tenants/{slug}/api-keys`
- `GET /api/v1/tenants/{slug}/api-keys`
- `DELETE /api/v1/tenants/{slug}/api-keys/{id}`
- `GET /api/v1/tenants/{slug}/usage`
- `GET /api/v1/tenants/{slug}/billing`
- `PATCH /api/v1/tenants/{slug}/billing`

Without a valid `X-Admin-Key`:
- Missing key: `401 Unauthorized`
- Invalid key: `403 Forbidden`

---

## API Keys (Per-Tenant)

API keys can be generated per tenant for future programmatic access.

### Generate a Key

```bash
curl -X POST https://nadakki-ai-suite.onrender.com/api/v1/tenants/credicefi/api-keys \
  -H "X-Admin-Key: nadakki_admin_2025_master" \
  -H "Content-Type: application/json" \
  -d '{"name": "production"}'
```

Response includes the full key (`nad_live_...`) **once only**.
Store it securely — only the prefix is stored in the database.

### List Keys

```bash
curl https://nadakki-ai-suite.onrender.com/api/v1/tenants/credicefi/api-keys \
  -H "X-Admin-Key: nadakki_admin_2025_master"
```

### Deactivate a Key

```bash
curl -X DELETE https://nadakki-ai-suite.onrender.com/api/v1/tenants/credicefi/api-keys/{key_id} \
  -H "X-Admin-Key: nadakki_admin_2025_master"
```

---

## Live Execution Gate

To execute agents in live mode (non-dry-run):

1. Global `LIVE_ENABLED=true` must be set (env var)
2. Per-tenant `meta_live_enabled` / `sendgrid_live_enabled` must be true (DB)
3. Request must include `role: "admin"` or `X-Role: admin` header
4. All relevant gates must be approved

---

## Rate Limiting

- **Global:** 100 requests/min per tenant (all endpoints)
- **Agent execution:** Per-plan monthly limits (starter: 100, pro: 1000, enterprise: unlimited)

Rate limit headers on every response:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
```

On limit exceeded: `429 Too Many Requests`
