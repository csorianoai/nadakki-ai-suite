# NADAKKI Google Ads MVP

Multi-tenant AI-powered Google Ads management platform for financial institutions.

## Architecture

```
WordPress Dashboard --> FastAPI REST API (27+ endpoints)
                            |
                      OrchestratorIA
                            |
                      WorkflowEngine (5 YAML workflows)
                            |
                    +-------+-------+
                    |       |       |
              Strategist  Budget  RSA Generator  Search Cleaner
                    |       |       |               |
                    +-------+-------+---------------+
                            |
                      ActionPlanExecutor
                            |
                      GoogleAdsConnector
                  (Policy > Saga > Execute)
                            |
                      Google Ads API
```

## Quick Start

```bash
# Clone
git clone https://github.com/YOUR_USER/nadakki-google-ads-mvp.git
cd nadakki-google-ads-mvp

# Install
pip install -r requirements.txt

# Run tests (64 tests)
python main.py

# Start API server
uvicorn main:app --reload --port 8000

# Open docs
# http://localhost:8000/docs
```

## Project Stats

| Metric | Value |
|--------|-------|
| Python LOC | 10,286 |
| YAML LOC | 881 |
| Components | 19 |
| Tests | 64 |
| API Endpoints | 43 |
| Workflows | 5 |
| Agents | 5 (4 + Orchestrator) |
| KB Rules | 10 |

## Components (19)

### Core Infrastructure (Day 1-2)
- `InMemoryDatabase` - Async SQLite with schema management
- `TenantCredentialVault` - Encrypted credential storage per tenant
- `GoogleAdsClientFactory` - Client creation with mock fallback
- `OperationRegistry` - Versioned operation definitions
- `IdempotencyStore` - Duplicate request prevention
- `GoogleAdsExecutor` - Retry + circuit breaker execution
- `PolicyEngine` - Budget limits, approval gates, content validation
- `TelemetrySidecar` - JSON logs + Prometheus metrics
- `SagaJournal` - Audit trail + compensation patterns
- `GoogleAdsConnector` - Full pipeline orchestration

### Knowledge + Agents (Day 3-4)
- `YamlKnowledgeStore` - YAML-based rules, benchmarks, guardrails
- `GoogleAdsStrategistIA` - Campaign strategy generation
- `GoogleAdsBudgetPacingIA` - Budget pacing analysis
- `RSAAdCopyGeneratorIA` - RSA ad copy with compliance
- `SearchTermsCleanerIA` - Search terms analysis + cleanup

### Workflows + API (Day 5-6)
- `WorkflowEngine` - YAML-driven multi-step workflows
- `OrchestratorIA` - High-level request routing + auto-triage
- `ActionPlanExecutor` - Plan execution with saga tracking
- `REST API` - 43 FastAPI endpoints

## API Endpoints

### Agents
- `POST /api/v1/agents/strategist/propose` - Generate strategy
- `POST /api/v1/agents/strategist/analyze` - Performance analysis
- `POST /api/v1/agents/budget-pacing/analyze` - Budget pacing
- `POST /api/v1/agents/rsa-generator/generate` - RSA ad copy
- `POST /api/v1/agents/search-cleaner/analyze` - Search terms

### Workflows
- `GET /api/v1/workflows` - List workflows
- `POST /api/v1/workflows/{id}/run` - Execute workflow

### Orchestrator
- `POST /api/v1/orchestrator/request` - High-level request
- `POST /api/v1/orchestrator/triage` - Auto-triage by metrics

### Dashboard
- `GET /api/v1/dashboard/{tenant_id}` - Full dashboard data

See full API docs at `http://localhost:8000/docs`

## Multi-Tenant Usage

```bash
# Add new financial institution
curl -X POST http://localhost:8000/api/v1/tenants/bank01/credentials \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"...","customer_id":"1234567890"}'

# Run optimization
curl -X POST http://localhost:8000/api/v1/orchestrator/request \
  -d '{"tenant_id":"bank01","request_type":"optimize","auto_approve":true}'

# Auto-triage
curl -X POST http://localhost:8000/api/v1/orchestrator/triage \
  -d '{"tenant_id":"bank01","metrics":{"cpa":200,"ctr":0.5,"budget_pacing":160}}'
```

## Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for:
- Docker deployment
- AWS Lambda
- EC2 with Nginx
- WordPress integration

## License

Proprietary - NADAKKI AI Suite
