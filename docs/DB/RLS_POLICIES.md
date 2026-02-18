# Row-Level Security (RLS) Policies

## Overview

All tenant-scoped tables use PostgreSQL Row-Level Security to enforce data isolation.
Each query only sees rows where `tenant_id` matches the current session's tenant context.

## How It Works

1. **Session variable**: Before each query, the application sets:
   ```sql
   SET LOCAL app.tenant_id = '<tenant_id>';
   ```
   This is scoped to the current transaction only.

2. **Helper function** (migration 003):
   ```sql
   CREATE FUNCTION current_tenant_id() RETURNS TEXT
   LANGUAGE sql STABLE
   AS $$ SELECT current_setting('app.tenant_id', true) $$;
   ```

3. **Policy** on each table:
   ```sql
   CREATE POLICY tenant_isolation ON <table>
     USING (tenant_id = current_tenant_id())
     WITH CHECK (tenant_id = current_tenant_id());
   ```

## Tables with RLS

| Table              | Migration | Policy Name       |
|--------------------|-----------|-------------------|
| audit_logs         | 001       | tenant_isolation  |
| users              | 003       | tenant_isolation  |
| oauth_tokens       | 003       | tenant_isolation  |
| agent_executions   | 003       | tenant_isolation  |
| audit_events       | 003       | tenant_isolation  |
| tenant_config      | 003       | tenant_isolation  |

## Application Layer

### RLS Middleware (`backend/db/rls.py`)
- Reads `X-Tenant-ID` header from every request
- Stores `tenant_id` on `request.state.tenant_id`
- Default tenant: `credicefi`

### Session Context (`services/db.py`)
- `get_session(tenant_id=...)` sets `SET LOCAL app.tenant_id` automatically
- All database operations should use this context manager

### Audit Middleware (`backend/middleware/audit.py`)
- Logs every request to `audit_events` table
- Uses tenant_id from `X-Tenant-ID` header

## Important Notes

- RLS is enforced at the **database level** — even raw SQL queries are filtered
- The `tenants` table itself does **not** have RLS (it's the parent lookup table)
- Superuser connections bypass RLS by default in PostgreSQL
- Application connects as a **non-superuser** role in production for RLS to be effective
- `current_setting('app.tenant_id', true)` returns NULL if not set (the `true` = missing_ok)

## Testing

Run RLS isolation tests:
```bash
DATABASE_URL=postgresql://... pytest tests/db/test_rls.py -v
```
