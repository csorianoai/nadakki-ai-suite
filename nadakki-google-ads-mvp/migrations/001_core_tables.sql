-- ============================================================================
-- NADAKKI AI SUITE - Migration 001: Core Tables
-- Multi-Tenant Google Ads Integration
-- ============================================================================
-- REUSABLE FOR: Multiple Financial Institutions
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- TENANT CREDENTIALS
-- ============================================================================

CREATE TABLE IF NOT EXISTS tenant_credentials (
    tenant_id VARCHAR(100) PRIMARY KEY,
    encrypted_data TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE tenant_credentials IS 'Encrypted OAuth credentials per tenant';
COMMENT ON COLUMN tenant_credentials.tenant_id IS 'Unique identifier for financial institution';
COMMENT ON COLUMN tenant_credentials.encrypted_data IS 'Fernet/KMS encrypted credentials JSON';

CREATE INDEX IF NOT EXISTS idx_tenant_creds_updated 
    ON tenant_credentials(updated_at);

-- ============================================================================
-- CREDENTIAL ACCESS LOG (Compliance/Audit)
-- ============================================================================

CREATE TABLE IF NOT EXISTS credential_access_log (
    id BIGSERIAL PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    details JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT
);

COMMENT ON TABLE credential_access_log IS 'Audit trail for credential access';

CREATE INDEX IF NOT EXISTS idx_cred_access_tenant 
    ON credential_access_log(tenant_id);
CREATE INDEX IF NOT EXISTS idx_cred_access_timestamp 
    ON credential_access_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_cred_access_action 
    ON credential_access_log(action);

-- ============================================================================
-- IDEMPOTENCY KEYS
-- ============================================================================

CREATE TABLE IF NOT EXISTS idempotency_keys (
    key VARCHAR(64) PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,
    operation_name VARCHAR(100) NOT NULL,
    result JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

COMMENT ON TABLE idempotency_keys IS 'Prevent duplicate operation execution';

CREATE INDEX IF NOT EXISTS idx_idempotency_tenant 
    ON idempotency_keys(tenant_id);
CREATE INDEX IF NOT EXISTS idx_idempotency_expires 
    ON idempotency_keys(expires_at);
CREATE INDEX IF NOT EXISTS idx_idempotency_operation 
    ON idempotency_keys(operation_name);

-- ============================================================================
-- TENANTS CONFIGURATION
-- ============================================================================

CREATE TABLE IF NOT EXISTS tenants (
    tenant_id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    plan VARCHAR(50) DEFAULT 'basic',
    status VARCHAR(50) DEFAULT 'active',
    settings JSONB DEFAULT '{}',
    google_ads_customer_id VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE tenants IS 'Financial institution configuration';
COMMENT ON COLUMN tenants.plan IS 'Subscription plan: basic, pro, enterprise';
COMMENT ON COLUMN tenants.status IS 'active, suspended, pending, archived';

CREATE INDEX IF NOT EXISTS idx_tenants_status 
    ON tenants(status);

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to tables with updated_at
DROP TRIGGER IF EXISTS update_tenant_credentials_updated_at ON tenant_credentials;
CREATE TRIGGER update_tenant_credentials_updated_at
    BEFORE UPDATE ON tenant_credentials
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_tenants_updated_at ON tenants;
CREATE TRIGGER update_tenants_updated_at
    BEFORE UPDATE ON tenants
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Insert demo tenant for testing
INSERT INTO tenants (tenant_id, name, display_name, plan, status) 
VALUES ('demo_tenant', 'Demo Financial Institution', 'Demo FI', 'basic', 'active')
ON CONFLICT (tenant_id) DO NOTHING;

-- ============================================================================
-- GRANTS (adjust for your database user)
-- ============================================================================

-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO nadakki_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO nadakki_app;
