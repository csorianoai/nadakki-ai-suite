"""RLS policies on all tenant-scoped tables

Revision ID: 003
Revises: 002
Create Date: 2026-02-18
"""
from alembic import op

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None

# Tables that need RLS (audit_logs already has it from 001)
_RLS_TABLES = ["users", "oauth_tokens", "agent_executions", "audit_events", "tenant_config"]


def upgrade() -> None:
    # Create helper function for cleaner policy definitions
    op.execute("""
        CREATE OR REPLACE FUNCTION current_tenant_id()
        RETURNS TEXT
        LANGUAGE sql STABLE
        AS $$ SELECT current_setting('app.tenant_id', true) $$
    """)

    for table in _RLS_TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"""
            CREATE POLICY tenant_isolation ON {table}
            USING (tenant_id = current_tenant_id())
            WITH CHECK (tenant_id = current_tenant_id())
        """)


def downgrade() -> None:
    for table in reversed(_RLS_TABLES):
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation ON {table}")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")

    op.execute("DROP FUNCTION IF EXISTS current_tenant_id()")
