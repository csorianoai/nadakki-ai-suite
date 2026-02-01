-- NADAKKI AI Suite - Migration 002: Saga Tables

CREATE TABLE IF NOT EXISTS sagas (
    saga_id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,
    workflow_name VARCHAR(100),
    input_data JSONB,
    status VARCHAR(50) NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_sagas_tenant ON sagas(tenant_id);
CREATE INDEX IF NOT EXISTS idx_sagas_status ON sagas(status);

CREATE TABLE IF NOT EXISTS saga_steps (
    step_id VARCHAR(36) PRIMARY KEY,
    saga_id VARCHAR(36),
    tenant_id VARCHAR(100) NOT NULL,
    operation_id VARCHAR(36),
    operation_name VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    payload JSONB,
    result JSONB,
    compensation_data JSONB,
    execution_time_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_saga_steps_saga ON saga_steps(saga_id);
CREATE INDEX IF NOT EXISTS idx_saga_steps_tenant ON saga_steps(tenant_id);
CREATE INDEX IF NOT EXISTS idx_saga_steps_status ON saga_steps(status);
