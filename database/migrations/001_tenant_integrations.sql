-- Migration 001: Tenant Integrations, OAuth State, Activity Log
-- Applied automatically by TokenStore.__init__

CREATE TABLE IF NOT EXISTS tenant_integrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id VARCHAR(100) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    user_id VARCHAR(255),
    user_name VARCHAR(255),
    user_email VARCHAR(255),
    page_id VARCHAR(100),
    page_name VARCHAR(255),
    ig_account_id VARCHAR(100),
    ads_customer_ids TEXT,
    analytics_property_id VARCHAR(100),
    youtube_channel_id VARCHAR(100),
    scopes TEXT,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tenant_id, platform)
);

CREATE TABLE IF NOT EXISTS oauth_state_store (
    state_key VARCHAR(255) PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,
    nonce VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS oauth_activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id VARCHAR(100),
    platform VARCHAR(50),
    action VARCHAR(50),
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
