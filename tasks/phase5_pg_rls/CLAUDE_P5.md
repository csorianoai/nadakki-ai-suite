# CLAUDE — PHASE 5 (PostgreSQL + RLS) — EXECUTION PACK

## GOAL
Replace JSONL audit + any tenant storage with PostgreSQL using strict Row Level Security (RLS).
Must be multi-tenant bank-grade.

## CONSTRAINTS
- Keep existing APIs working.
- Default behavior stays DRY_RUN and safe.
- Local dev must still run.
- Use env var DATABASE_URL; if missing, fallback to current JSONL behavior (temporary) to avoid breaking deploy.

## TASKS (DO IN ORDER)

### P5-1) Add DB layer (SQLAlchemy or asyncpg)
- Create services/db.py:
  - create_engine / async engine
  - session factory
  - health check function db_ping()

### P5-2) Schema + migrations (Alembic preferred)
Tables:
1) tenants (id, name, created_at)
2) audit_logs (
   id uuid pk,
   trace_id text,
   tenant_id text not null,
   agent_id text not null,
   mode text,
   status text,
   http_status int,
   latency_ms int,
   user_id text null,
   error text null,
   created_at timestamptz default now()
)

Indexes:
- audit_logs(tenant_id, created_at desc)
- audit_logs(agent_id, created_at desc)
- audit_logs(trace_id)

### P5-3) RLS
Implement Postgres RLS:
- Enable RLS on audit_logs.
- Policy: tenant_id = current_setting('app.tenant_id', true)
- In request handling, set `SET LOCAL app.tenant_id = :tenant_id` per transaction.

### P5-4) Update audit logger to write to DB when DATABASE_URL exists
- services/audit_logger.py:
  - write_log() writes to DB if available; else JSONL fallback.
- routers/audit_router.py:
  - GET /api/v1/audit/logs reads from DB if available; else JSONL fallback.

### P5-5) Add /api/v1/health/db (optional)
- Return ok/failed and latency.

### P5-6) Tests + curl verification
Provide curl examples to verify:
- Insert audit entry via agent execute
- Query logs filtered by tenant_id
- Confirm tenant isolation by trying another tenant

### P5-7) Render readiness
- Ensure env variables documented:
  - DATABASE_URL
  - LIVE_ENABLED
  - ALLOWED_ORIGINS
- No secrets in repo.

## DELIVERABLES
- PR with migrations + RLS + DB audit storage
- Short README snippet for setup
- Verified curl commands with expected outputs (200 + count>=1)
