"""Multi-tenant schema: users, oauth_tokens, agent_executions, audit_events, tenant_config

Revision ID: 002
Revises: 001
Create Date: 2026-02-18
"""
from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Extend tenants table with slug and plan ---
    op.add_column("tenants", sa.Column("slug", sa.String, unique=True, nullable=True))
    op.add_column("tenants", sa.Column("plan", sa.String, server_default="starter", nullable=True))

    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.String, sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("email", sa.String, nullable=False),
        sa.Column("role", sa.String, server_default="viewer"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"])

    # --- oauth_tokens ---
    op.create_table(
        "oauth_tokens",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.String, sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("platform", sa.String(50), nullable=False),
        sa.Column("access_token", sa.Text, nullable=False),
        sa.Column("refresh_token", sa.Text, nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_oauth_tokens_tenant_id", "oauth_tokens", ["tenant_id"])
    op.create_index("ix_oauth_tokens_tenant_platform", "oauth_tokens", ["tenant_id", "platform"])

    # --- agent_executions ---
    op.create_table(
        "agent_executions",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.String, sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("agent_id", sa.String, nullable=False),
        sa.Column("dry_run", sa.Boolean, server_default=sa.text("true")),
        sa.Column("result", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_agent_executions_tenant_id", "agent_executions", ["tenant_id"])
    op.create_index("ix_agent_executions_agent_id", "agent_executions", ["agent_id"])

    # --- audit_events ---
    op.create_table(
        "audit_events",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.String, sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("user_id", sa.String, nullable=True),
        sa.Column("action", sa.String, nullable=True),
        sa.Column("endpoint", sa.String, nullable=True),
        sa.Column("method", sa.String(10), nullable=True),
        sa.Column("status_code", sa.Integer, nullable=True),
        sa.Column("latency_ms", sa.Integer, nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_audit_events_tenant_id", "audit_events", ["tenant_id"])
    op.create_index("ix_audit_events_timestamp", "audit_events", [sa.text("timestamp DESC")])

    # --- tenant_config ---
    op.create_table(
        "tenant_config",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.String, sa.ForeignKey("tenants.id"), nullable=False, unique=True),
        sa.Column("meta_live_enabled", sa.Boolean, server_default=sa.text("false")),
        sa.Column("sendgrid_live_enabled", sa.Boolean, server_default=sa.text("false")),
    )

    # --- Insert default tenant credicefi ---
    op.execute(
        "INSERT INTO tenants (id, name, slug, plan) "
        "VALUES ('credicefi', 'CredICEFI', 'credicefi', 'enterprise') "
        "ON CONFLICT (id) DO UPDATE SET slug = 'credicefi', plan = 'enterprise'"
    )
    op.execute(
        "INSERT INTO tenant_config (tenant_id, meta_live_enabled, sendgrid_live_enabled) "
        "VALUES ('credicefi', false, false) "
        "ON CONFLICT (tenant_id) DO NOTHING"
    )


def downgrade() -> None:
    op.drop_table("tenant_config")
    op.drop_index("ix_audit_events_timestamp")
    op.drop_index("ix_audit_events_tenant_id")
    op.drop_table("audit_events")
    op.drop_index("ix_agent_executions_agent_id")
    op.drop_index("ix_agent_executions_tenant_id")
    op.drop_table("agent_executions")
    op.drop_index("ix_oauth_tokens_tenant_platform")
    op.drop_index("ix_oauth_tokens_tenant_id")
    op.drop_table("oauth_tokens")
    op.drop_index("ix_users_tenant_id")
    op.drop_table("users")
    op.execute("ALTER TABLE tenants DROP COLUMN IF EXISTS plan")
    op.execute("ALTER TABLE tenants DROP COLUMN IF EXISTS slug")
