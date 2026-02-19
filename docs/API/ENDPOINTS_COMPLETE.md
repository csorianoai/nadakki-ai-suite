# NADAKKI AI Suite - Complete API Endpoints Reference

**Version:** 5.4.4
**Base URL:** `https://nadakki-ai-suite.onrender.com`

---

## Authentication

All admin endpoints require `X-Admin-Key` header.
All tenant-scoped endpoints use `X-Tenant-ID` header (default: `credicefi`).

---

## Health & System

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | None | Health check with DB, RLS, gates, uptime |
| GET | `/api/v1/health` | None | Alias for `/health` |
| GET | `/api/v1/health/db` | None | Database ping |
| GET | `/api/v1/system/info` | None | Version, uptime, DB provider, totals |

## Agent Discovery

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/agents` | None | List agents with filters |
| GET | `/api/agents` | None | Alias |
| GET | `/api/catalog` | None | Alias |
| GET | `/api/ai-studio/agents` | None | Alias |
| GET | `/api/catalog/{module}/agents` | None | Module-filtered agents |
| GET | `/api/v1/agents/{id}/analysis` | None | Deep analysis of an agent |
| GET | `/api/v1/reality` | None | Discovery stats report |

## Agent Execution

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/agents/execute` | X-Tenant-ID | Execute agent (body-based, flexible ID) |
| POST | `/api/v1/agents/{id}/execute` | X-Tenant-ID | Execute agent (legacy path-based) |

## Social & OAuth

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/social/connections` | None | List social platform connections |
| GET | `/api/social/status/{tenant_id}` | None | Platform status for tenant |
| GET | `/api/v1/social/status` | None | Global dry_run / live flags |
| GET | `/auth/meta/login` | None | Meta OAuth login redirect |
| GET | `/auth/meta/callback` | None | Meta OAuth callback |
| GET | `/auth/google/login` | None | Google OAuth login redirect |
| GET | `/auth/google/callback` | None | Google OAuth callback |

## Debug & Config

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/config` | None | LIVE_ENABLED env status |
| GET | `/api/v1/db/status` | None | DB tables, tenants, RLS, gates |
| GET | `/api/v1/db/audit-events` | None | Recent 20 audit events |

## Tenant Management

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/tenants/onboard` | X-Admin-Key | Create tenant + admin user + config |
| PATCH | `/api/v1/tenants/{slug}/config` | X-Admin-Key | Update live flags per tenant |

## Gates

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/gates` | None | List all gates with status |
| POST | `/api/v1/gates/{gate_id}/approve` | X-Admin-Key | Approve a gate |
| POST | `/api/v1/gates/{gate_id}/reject` | X-Admin-Key | Reject a gate |

## API Keys

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/tenants/{slug}/api-keys` | X-Admin-Key | Generate new API key |
| GET | `/api/v1/tenants/{slug}/api-keys` | X-Admin-Key | List keys (prefix only) |
| DELETE | `/api/v1/tenants/{slug}/api-keys/{id}` | X-Admin-Key | Deactivate a key |

## Usage Tracking

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/tenants/{slug}/usage` | X-Admin-Key | Current month usage + limits |

## Billing

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/billing/plans` | None | List available plans |
| GET | `/api/v1/tenants/{slug}/billing` | X-Admin-Key | Tenant billing info |
| PATCH | `/api/v1/tenants/{slug}/billing` | X-Admin-Key | Change plan (stub) |

## Audit

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/audit/events` | None | Audit events list |

## Rate Limiting

All endpoints (except `/health`, `/docs`) are rate limited to **100 requests/min per tenant**.

Response headers:
- `X-RateLimit-Limit`: 100
- `X-RateLimit-Remaining`: remaining requests
- `Retry-After`: seconds to wait (on 429)

## Plan Execution Limits

| Plan | Executions/month | Price |
|------|-------------------|-------|
| starter | 100 | $9.99 |
| pro | 1,000 | $29.99 |
| enterprise | unlimited | $99.99 |

Exceeding the limit returns `429 Too Many Requests`.

---

## Database Tables

tenants, users, oauth_tokens, agent_executions, audit_events,
tenant_config, gates, api_keys, usage_tracking

All tenant-scoped tables have Row Level Security (RLS) enabled.
