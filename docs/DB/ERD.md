# Database ERD — Nadakki AI Suite

## Tables

```
┌─────────────────────┐
│      tenants         │
├─────────────────────┤
│ id          TEXT PK  │
│ name        TEXT     │
│ slug        TEXT UQ  │
│ plan        TEXT     │
│ created_at  TIMESTZ  │
└──────────┬──────────┘
           │
           │ 1:N
     ┌─────┼─────────────────┬──────────────────┬──────────────────┬──────────────────┐
     │     │                 │                  │                  │                  │
     ▼     ▼                 ▼                  ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│    users     │  │  oauth_tokens    │  │agent_executions  │  │  audit_events    │  │  tenant_config   │
├──────────────┤  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤
│ id      SERIAL│  │ id      SERIAL  │  │ id      SERIAL  │  │ id      SERIAL  │  │ id      SERIAL  │
│ tenant_id FK │  │ tenant_id FK    │  │ tenant_id FK    │  │ tenant_id FK    │  │ tenant_id FK UQ │
│ email   TEXT │  │ platform TEXT   │  │ agent_id TEXT   │  │ user_id  TEXT   │  │ meta_live  BOOL │
│ role    TEXT │  │ access_token TXT│  │ dry_run  BOOL   │  │ action   TEXT   │  │ sendgrid   BOOL │
│ created_at   │  │ refresh_token   │  │ result   TEXT   │  │ endpoint TEXT   │  └──────────────────┘
└──────────────┘  │ expires_at      │  │ created_at      │  │ method   TEXT   │
                  │ created_at      │  └──────────────────┘  │ status_code INT │
                  └──────────────────┘                        │ latency_ms INT  │
                                                              │ timestamp       │
                                                              └──────────────────┘

┌──────────────────┐
│   audit_logs     │  (from migration 001 — agent execution audit)
├──────────────────┤
│ id        UUID PK│
│ trace_id  TEXT   │
│ tenant_id TEXT   │
│ agent_id  TEXT   │
│ mode      TEXT   │
│ status    TEXT   │
│ http_status INT  │
│ latency_ms INT   │
│ user_id   TEXT   │
│ error     TEXT   │
│ created_at TIMESTZ│
└──────────────────┘
```

## Foreign Keys

| Child Table        | Column      | References     |
|--------------------|-------------|----------------|
| users              | tenant_id   | tenants.id     |
| oauth_tokens       | tenant_id   | tenants.id     |
| agent_executions   | tenant_id   | tenants.id     |
| audit_events       | tenant_id   | tenants.id     |
| tenant_config      | tenant_id   | tenants.id     |

## Indexes

| Table              | Index Name                         | Columns                      |
|--------------------|------------------------------------|------------------------------|
| users              | ix_users_tenant_id                 | tenant_id                    |
| oauth_tokens       | ix_oauth_tokens_tenant_id          | tenant_id                    |
| oauth_tokens       | ix_oauth_tokens_tenant_platform    | tenant_id, platform          |
| agent_executions   | ix_agent_executions_tenant_id      | tenant_id                    |
| agent_executions   | ix_agent_executions_agent_id       | agent_id                     |
| audit_events       | ix_audit_events_tenant_id          | tenant_id                    |
| audit_events       | ix_audit_events_timestamp          | timestamp DESC               |
| audit_logs         | ix_audit_logs_tenant_created       | tenant_id, created_at DESC   |
| audit_logs         | ix_audit_logs_agent_created        | agent_id, created_at DESC    |
| audit_logs         | ix_audit_logs_trace_id             | trace_id                     |

## Migrations

| Revision | Description                              |
|----------|------------------------------------------|
| 001      | tenants + audit_logs + RLS on audit_logs |
| 002      | users, oauth_tokens, agent_executions, audit_events, tenant_config |
| 003      | RLS policies on all tenant-scoped tables |
