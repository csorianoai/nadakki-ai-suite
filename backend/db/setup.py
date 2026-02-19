"""
Database setup — creates tables and seeds default data on startup.
Runs against Supabase PostgreSQL via DATABASE_URL.
Each statement is executed individually (asyncpg requirement).
"""

import logging
from sqlalchemy import text

logger = logging.getLogger("nadakki.db.setup")

# ── TAREA 1: Create all tables (one statement each) ─────────────────────────

_TABLE_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS tenants (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      name TEXT NOT NULL,
      slug TEXT UNIQUE NOT NULL,
      plan TEXT DEFAULT 'starter',
      created_at TIMESTAMPTZ DEFAULT now()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS users (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      tenant_id UUID REFERENCES tenants(id),
      email TEXT NOT NULL,
      role TEXT DEFAULT 'analyst',
      created_at TIMESTAMPTZ DEFAULT now()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS oauth_tokens (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      tenant_id UUID REFERENCES tenants(id),
      platform TEXT NOT NULL,
      access_token TEXT,
      refresh_token TEXT,
      expires_at TIMESTAMPTZ,
      created_at TIMESTAMPTZ DEFAULT now()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS agent_executions (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      tenant_id UUID REFERENCES tenants(id),
      agent_id TEXT NOT NULL,
      dry_run BOOLEAN DEFAULT true,
      result JSONB,
      created_at TIMESTAMPTZ DEFAULT now()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS audit_events (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      tenant_id UUID,
      user_id UUID,
      action TEXT,
      endpoint TEXT,
      method TEXT,
      status_code INTEGER,
      timestamp TIMESTAMPTZ DEFAULT now()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS tenant_config (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      tenant_id UUID REFERENCES tenants(id) UNIQUE,
      meta_live_enabled BOOLEAN DEFAULT false,
      sendgrid_live_enabled BOOLEAN DEFAULT false,
      updated_at TIMESTAMPTZ DEFAULT now()
    )
    """,
]

# ── TAREA 2: Default tenant ─────────────────────────────────────────────────

_SEED_STATEMENTS = [
    """
    INSERT INTO tenants (name, slug, plan)
    VALUES ('CrediCefi', 'credicefi', 'pro')
    ON CONFLICT (slug) DO NOTHING
    """,
    """
    INSERT INTO tenant_config (tenant_id, meta_live_enabled, sendgrid_live_enabled)
    SELECT id, false, false FROM tenants WHERE slug = 'credicefi'
    ON CONFLICT (tenant_id) DO NOTHING
    """,
]

# ── TAREA 3: RLS policies ───────────────────────────────────────────────────

_RLS_TABLES = ["users", "oauth_tokens", "agent_executions", "audit_events", "tenant_config"]


def _rls_statements(table: str) -> list:
    return [
        f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY",
        f"""
        DO $$
        BEGIN
          IF NOT EXISTS (
            SELECT 1 FROM pg_policies WHERE tablename = '{table}' AND policyname = 'tenant_isolation'
          ) THEN
            CREATE POLICY tenant_isolation ON {table}
              USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
          END IF;
        END $$
        """,
    ]


async def run_setup(engine) -> dict:
    """
    Run full DB setup: create tables, seed data, enable RLS.
    Returns a status dict.
    """
    results = {"tables": False, "seed": False, "rls": False, "errors": []}

    async with engine.begin() as conn:
        # 1. Create tables
        try:
            for stmt in _TABLE_STATEMENTS:
                await conn.execute(text(stmt))
            results["tables"] = True
            logger.info("Tables created/verified")
        except Exception as e:
            results["errors"].append(f"tables: {e}")
            logger.error("Table creation failed: %s", e)

        # 2. Seed default tenant
        try:
            for stmt in _SEED_STATEMENTS:
                await conn.execute(text(stmt))
            results["seed"] = True
            logger.info("Default tenant seeded")
        except Exception as e:
            results["errors"].append(f"seed: {e}")
            logger.error("Seed failed: %s", e)

        # 3. RLS policies
        try:
            for table in _RLS_TABLES:
                for stmt in _rls_statements(table):
                    await conn.execute(text(stmt))
            results["rls"] = True
            logger.info("RLS policies applied on %d tables", len(_RLS_TABLES))
        except Exception as e:
            results["errors"].append(f"rls: {e}")
            logger.error("RLS setup failed: %s", e)

    return results
