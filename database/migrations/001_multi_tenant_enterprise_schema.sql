-- NADAKKI DATABASE SCHEMA v6.0
-- PostgreSQL 16+ - Multi-Tenant Enterprise Grade

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS uuid-ossp;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

CREATE TABLE IF NOT EXISTS institutions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    country VARCHAR(2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    domain VARCHAR(100) UNIQUE,
    api_key_hash VARCHAR(255) UNIQUE NOT NULL,
    webhook_secret_hash VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active',
    pci_dss_level SMALLINT DEFAULT 1,
    gdpr_compliant BOOLEAN DEFAULT TRUE,
    aml_screening BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    auth0_id VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    status VARCHAR(20) DEFAULT 'active',
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_institution_email UNIQUE (institution_id, email)
);

CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    webhook_secret_hash VARCHAR(255),
    name VARCHAR(100),
    last_used TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    expires_at TIMESTAMPTZ,
    CONSTRAINT unique_institution_api_key UNIQUE (institution_id, key_hash)
);

CREATE TABLE IF NOT EXISTS credit_evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    applicant_id VARCHAR(255) NOT NULL,
    similarity_score NUMERIC(3, 2),
    risk_level VARCHAR(20),
    recommendation VARCHAR(50),
    engine_version VARCHAR(20) DEFAULT '6.0',
    evaluated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_institution_applicant UNIQUE (institution_id, applicant_id, evaluated_at)
);

CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    amount BIGINT NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(50) DEFAULT 'pending',
    stripe_payment_intent_id VARCHAR(255),
    idempotency_key VARCHAR(255) UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(255),
    changes JSONB,
    ip_address INET,
    user_agent TEXT,
    status_code INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX CONCURRENTLY idx_institutions_status ON institutions(status);
CREATE INDEX CONCURRENTLY idx_institutions_type ON institutions(type);
CREATE INDEX CONCURRENTLY idx_users_institution_email ON users(institution_id, email);
CREATE INDEX CONCURRENTLY idx_api_keys_institution ON api_keys(institution_id);
CREATE INDEX CONCURRENTLY idx_evaluations_institution ON credit_evaluations(institution_id, evaluated_at DESC);
CREATE INDEX CONCURRENTLY idx_payments_institution_status ON payments(institution_id, status);
CREATE INDEX CONCURRENTLY idx_audit_logs_institution ON audit_logs(institution_id, created_at DESC);

ALTER TABLE institutions ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE credit_evaluations ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY institutions_isolation ON institutions
    USING (id::text = current_setting('app.current_institution_id', true));
CREATE POLICY users_isolation ON users
    USING (institution_id::text = current_setting('app.current_institution_id', true));
CREATE POLICY api_keys_isolation ON api_keys
    USING (institution_id::text = current_setting('app.current_institution_id', true));
CREATE POLICY credit_evaluations_isolation ON credit_evaluations
    USING (institution_id::text = current_setting('app.current_institution_id', true));
CREATE POLICY payments_isolation ON payments
    USING (institution_id::text = current_setting('app.current_institution_id', true));
CREATE POLICY audit_logs_isolation ON audit_logs
    USING (institution_id::text = current_setting('app.current_institution_id', true));

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS \$\$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
\$\$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_institutions ON institutions
    BEFORE UPDATE FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trigger_update_users ON users
    BEFORE UPDATE FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trigger_update_payments ON payments
    BEFORE UPDATE FOR EACH ROW EXECUTE FUNCTION update_updated_at();
