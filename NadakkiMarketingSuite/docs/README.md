# Nadakki Marketing Suite v4.0

## Multi-Tenant Marketing Platform

### Features
- Multi-tenant architecture (múltiples instituciones financieras)
- Campaign management
- Social media connections (7 platforms)
- Scheduler (APScheduler)
- Analytics and metrics

### Quick Start
```bash
pip install -r requirements.txt
python tests/test_complete.py
uvicorn backend.main:app --reload
```

### API Endpoints
- POST /api/v1/tenants - Create tenant
- GET /api/v1/tenants - List tenants
- POST /api/v1/campaigns - Create campaign
- POST /api/v1/scheduler/start - Start scheduler
- GET /api/v1/metrics - Get metrics
