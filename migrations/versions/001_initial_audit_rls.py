"""Initial audit tables + RLS

Revision ID: 001
Revises: None
Create Date: 2026-02-18
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- tenants ---
    op.create_table(
        "tenants",
        sa.Column("id", sa.Text, primary_key=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # --- audit_logs ---
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.dialects.postgresql.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("trace_id", sa.Text, nullable=False),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("agent_id", sa.Text, nullable=False),
        sa.Column("mode", sa.Text),
        sa.Column("status", sa.Text),
        sa.Column("http_status", sa.Integer),
        sa.Column("latency_ms", sa.Integer),
        sa.Column("user_id", sa.Text, nullable=True),
        sa.Column("error", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # --- indexes ---
    op.create_index("ix_audit_logs_tenant_created", "audit_logs", ["tenant_id", sa.text("created_at DESC")])
    op.create_index("ix_audit_logs_agent_created", "audit_logs", ["agent_id", sa.text("created_at DESC")])
    op.create_index("ix_audit_logs_trace_id", "audit_logs", ["trace_id"])

    # --- RLS ---
    op.execute("ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY tenant_isolation ON audit_logs
        USING (tenant_id = current_setting('app.tenant_id', true))
        WITH CHECK (tenant_id = current_setting('app.tenant_id', true))
    """)

    # Insert default tenant
    op.execute("INSERT INTO tenants (id, name) VALUES ('default', 'Default Tenant') ON CONFLICT DO NOTHING")


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON audit_logs")
    op.execute("ALTER TABLE audit_logs DISABLE ROW LEVEL SECURITY")
    op.drop_index("ix_audit_logs_trace_id")
    op.drop_index("ix_audit_logs_agent_created")
    op.drop_index("ix_audit_logs_tenant_created")
    op.drop_table("audit_logs")
    op.drop_table("tenants")
