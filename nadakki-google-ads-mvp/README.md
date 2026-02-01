# NADAKKI AI Suite - Google Ads Multi-Tenant Integration

## 🎯 Overview

Enterprise-grade Google Ads integration platform designed for **multiple financial institutions**. This system provides:

- **Multi-tenant architecture** - Each institution has isolated credentials and policies
- **Intelligent agents** - Automated budget optimization, ad copy generation, search term cleanup
- **Policy enforcement** - Compliance rules per tenant (critical for financial services)
- **Audit trail** - Complete operation logging for regulatory compliance
- **Workflow engine** - YAML-based automated optimization cycles

## 📁 Project Structure

```
nadakki-google-ads-mvp/
├── core/
│   ├── security/
│   │   └── tenant_vault.py       # Credential encryption & management
│   ├── google_ads/
│   │   ├── client_factory.py     # Connection pool & auto-refresh
│   │   ├── executor.py           # Resilient execution (circuit breaker)
│   │   └── connector.py          # Complete pipeline facade
│   ├── operations/
│   │   └── registry.py           # Typed operations with validation
│   ├── reliability/
│   │   └── idempotency.py        # Duplicate prevention
│   ├── policies/
│   │   └── engine.py             # Multi-tenant policy validation
│   ├── observability/
│   │   └── telemetry.py          # Structured logging & metrics
│   ├── saga/
│   │   └── journal.py            # Audit trail & compensation
│   ├── agents/
│   │   └── action_plan.py        # Standardized agent output
│   ├── execution/
│   │   └── action_plan_executor.py  # Execute agent plans
│   └── workflows/
│       └── engine.py             # YAML workflow execution
├── agents/
│   └── marketing/
│       ├── budget_pacing_agent.py
│       ├── rsa_copy_generator_agent.py
│       ├── search_terms_cleaner_agent.py
│       └── orchestrator_agent.py
├── config/
│   ├── policies/
│   │   └── {tenant_id}.yaml      # Per-tenant policies
│   └── workflows/
│       ├── daily_optimization.yaml
│       ├── budget_adjustment.yaml
│       └── health_check.yaml
├── migrations/
│   ├── 001_core_tables.sql
│   └── 002_saga_tables.sql
├── tests/
│   ├── unit/
│   └── integration/
├── main.py                       # FastAPI application
├── requirements.txt
└── .env.example
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10+
- PostgreSQL 13+
- Google Ads API access (Developer Token)

### 2. Installation

```bash
# Clone and setup
cd nadakki-google-ads-mvp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your credentials
```

### 3. Database Setup

```bash
# Run migrations
psql -U postgres -d nadakki_ads -f migrations/001_core_tables.sql
psql -U postgres -d nadakki_ads -f migrations/002_saga_tables.sql
```

### 4. Start the Server

```bash
python -m uvicorn main:app --reload --port 8000
```

### 5. Access API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔐 Multi-Tenant Security

Each financial institution (tenant) has:

1. **Isolated credentials** - Encrypted at rest with Fernet (upgradeable to KMS)
2. **Custom policies** - Budget limits, prohibited keywords, approval gates
3. **Separate audit logs** - Full compliance trail
4. **Rate limiting** - Per-tenant operation limits

### Adding a New Tenant

```python
# 1. Store OAuth credentials
POST /tenants/{tenant_id}/credentials
{
    "tenant_id": "new_bank",
    "refresh_token": "...",
    "customer_id": "1234567890",
    "manager_customer_id": "9876543210"  # Optional for MCC
}

# 2. Create policy file: config/policies/new_bank.yaml
# Copy from demo_tenant.yaml and customize
```

## 🤖 Available Agents

### 1. Budget Pacing Agent
Analyzes campaign spending patterns and recommends budget adjustments.

```python
from agents.marketing.budget_pacing_agent import GoogleAdsBudgetPacingAgent

agent = GoogleAdsBudgetPacingAgent(connector, policy_engine)
plan = await agent.analyze_and_plan(tenant_id="bank_a")
# Returns ActionPlan with update_budget operations
```

### 2. RSA Copy Generator Agent
Generates Responsive Search Ad headlines and descriptions.

```python
from agents.marketing.rsa_copy_generator_agent import RSAAdCopyGeneratorAgent

agent = RSAAdCopyGeneratorAgent(policy_engine)
plan = await agent.generate_ad_copy(
    tenant_id="bank_a",
    product_info={
        "name": "Home Loans",
        "benefit": "Low rates",
        "category": "Mortgages"
    }
)
```

### 3. Search Terms Cleaner Agent
Identifies wasteful search terms and recommends negative keywords.

```python
from agents.marketing.search_terms_cleaner_agent import SearchTermsCleanerAgent

agent = SearchTermsCleanerAgent(connector)
plan = await agent.analyze_and_clean(tenant_id="bank_a")
```

### 4. Orchestrator Agent
Coordinates multiple agents for comprehensive optimization.

```python
from agents.marketing.orchestrator_agent import GoogleAdsOrchestratorAgent

orchestrator = GoogleAdsOrchestratorAgent(workflow_engine, connector, agents, policy_engine)
result = await orchestrator.run_optimization_cycle(
    tenant_id="bank_a",
    objective=OptimizationObjective.BUDGET_EFFICIENCY
)
```

## 📋 API Endpoints

### Operations
```
POST /tenants/{tenant_id}/operations     # Execute any operation
GET  /tenants/{tenant_id}/campaigns      # Get campaign metrics
POST /tenants/{tenant_id}/budgets/{id}   # Update budget
```

### Workflows
```
POST /tenants/{tenant_id}/workflows      # Start workflow
GET  /tenants/{tenant_id}/workflows/{id} # Get status
GET  /tenants/{tenant_id}/workflows      # List executions
```

### Optimization
```
POST /tenants/{tenant_id}/optimize       # Run optimization cycle
GET  /tenants/{tenant_id}/recommendations # Get recommendations
```

### Approvals
```
GET  /tenants/{tenant_id}/approvals      # List pending
POST /tenants/{tenant_id}/approvals      # Approve/reject
```

## 🔄 Workflow YAML Examples

### Daily Optimization
```yaml
name: daily_optimization
steps:
  - name: fetch_metrics
    type: operation
    operation: get_campaign_metrics@v1
    next_step: analyze_budget_pacing
    
  - name: analyze_budget_pacing
    type: agent
    agent: budget_pacing_agent
    next_step: analyze_search_terms
```

## 🛡️ Policy Configuration

Each tenant has a YAML policy file:

```yaml
tenant_id: "bank_a"
budget_limits:
  daily_max_usd: 500
  change_max_percent: 30

keyword_rules:
  prohibited:
    - "guaranteed approval"
    - "no credit check"

approval_gates:
  - rule: "budget_change > 20%"
    requires: "human_approval"
```

## 📊 Monitoring

### Metrics Endpoint
```
GET /metrics  # Prometheus-compatible
```

### Log Format
```json
{
    "timestamp": "2026-01-31T14:30:00Z",
    "level": "INFO",
    "event": "operation",
    "tenant_id": "bank_a",
    "operation_id": "uuid",
    "trace_id": "uuid",
    "success": true,
    "execution_time_ms": 150
}
```

## 🧪 Testing

```bash
# Run unit tests
pytest tests/unit -v

# Run integration tests
pytest tests/integration -v

# Run with coverage
pytest --cov=core --cov=agents tests/
```

## 🚀 Deployment Phases

| Phase | Duration | Focus |
|-------|----------|-------|
| 1 | Day 1 | Core Infrastructure (Vault, ClientFactory, Registry) |
| 2 | Day 2 | Executor, Policy, Connector, Telemetry |
| 3 | Day 3 | ActionPlan, Budget Pacing Agent |
| 4 | Day 4 | RSA Copy Agent, Search Terms Agent |
| 5 | Day 5 | Workflow Engine |
| 6 | Day 6 | Orchestrator, Workflow YAMLs |
| 7 | Day 7 | Testing, Security Hardening, Go Live |

## 📝 Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/nadakki_ads

# Google Ads
GOOGLE_ADS_DEVELOPER_TOKEN=your_token
NADAKKI_GOOGLE_CLIENT_ID=your_client_id
NADAKKI_GOOGLE_CLIENT_SECRET=your_secret
GOOGLE_ADS_API_VERSION=v15

# Security
CREDENTIAL_ENCRYPTION_KEY=32_byte_key

# Application
APP_ENV=production
LOG_LEVEL=INFO
```

## 🤝 Contributing

1. Follow the existing code patterns
2. Add tests for new features
3. Update documentation
4. Run linting and tests before commits

## 📄 License

Proprietary - NADAKKI AI Suite

---

**Built for Financial Institutions** 🏦
