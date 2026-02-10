# ═══════════════════════════════════════════════════════════════════════════════
# NADAKKI Google Ads MVP - Deployment Guide
# docs/DEPLOYMENT.md
# ═══════════════════════════════════════════════════════════════════════════════

# 🚀 Deployment Guide

## Architecture Overview

```
                    ┌─────────────────┐
                    │   WordPress     │
                    │   Dashboard     │
                    └───────┬─────────┘
                            │ REST API
                    ┌───────▼─────────┐
                    │   FastAPI App   │
                    │   (main.py)     │
                    └───────┬─────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
    ┌─────────▼───┐  ┌─────▼─────┐  ┌───▼─────────┐
    │ Orchestrator│  │ Workflow  │  │   Agents    │
    │      IA     │  │  Engine   │  │ (4 agents)  │
    └─────────────┘  └───────────┘  └─────────────┘
              │             │             │
              └─────────────┼─────────────┘
                            │
                    ┌───────▼─────────┐
                    │   Connector     │
                    │   (Pipeline)    │
                    └───────┬─────────┘
                            │
          ┌────────┬────────┼────────┬────────┐
          │        │        │        │        │
       Policy  Idempot.  Executor  Saga   Telemetry
       Engine   Store    (Retry)  Journal  Sidecar
                            │
                    ┌───────▼─────────┐
                    │  Google Ads API  │
                    └─────────────────┘
```

---

## 1. Local Development

### Prerequisites
- Python 3.9+
- pip

### Setup
```bash
cd nadakki-google-ads-mvp
pip install -r requirements.txt

# Run tests
python main.py

# Start API server
uvicorn main:app --reload --port 8000

# Open API docs
# http://localhost:8000/docs
```

### Environment Variables
```bash
# Optional — database URL (defaults to in-memory SQLite)
export DATABASE_URL=""

# Google Ads API credentials (for production)
export GOOGLE_ADS_DEVELOPER_TOKEN="your_developer_token"
export GOOGLE_ADS_CLIENT_ID="your_client_id"
export GOOGLE_ADS_CLIENT_SECRET="your_client_secret"
```

---

## 2. Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build & Run
```bash
docker build -t nadakki-google-ads-mvp .
docker run -p 8000:8000 \
  -e DATABASE_URL="" \
  -e GOOGLE_ADS_DEVELOPER_TOKEN="your_token" \
  nadakki-google-ads-mvp
```

### Docker Compose (with PostgreSQL)
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/nadakki
      - GOOGLE_ADS_DEVELOPER_TOKEN=${GOOGLE_ADS_DEVELOPER_TOKEN}
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: nadakki
      POSTGRES_PASSWORD: password
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

---

## 3. AWS Lambda Deployment

### Handler (lambda_handler.py)
```python
from mangum import Mangum
from main import app

handler = Mangum(app, lifespan="auto")
```

### SAM Template
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Globals:
  Function:
    Timeout: 30
    MemorySize: 512

Resources:
  NadakkiFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: lambda_handler.handler
      Runtime: python3.11
      CodeUri: .
      Events:
        ApiEvent:
          Type: HttpApi
          Properties:
            Path: /{proxy+}
            Method: ANY
      Environment:
        Variables:
          DATABASE_URL: ""
```

### Deploy
```bash
pip install mangum
sam build
sam deploy --guided
```

---

## 4. Production with EC2

### Setup Script
```bash
#!/bin/bash
sudo apt update
sudo apt install -y python3 python3-pip nginx certbot python3-certbot-nginx

# Clone and install
cd /opt
git clone <your-repo> nadakki
cd nadakki/nadakki-google-ads-mvp
pip3 install -r requirements.txt
pip3 install gunicorn

# Systemd service
cat > /etc/systemd/system/nadakki.service << 'EOF'
[Unit]
Description=NADAKKI Google Ads MVP
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/nadakki/nadakki-google-ads-mvp
ExecStart=/usr/local/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000
Restart=always
Environment=DATABASE_URL=

[Install]
WantedBy=multi-user.target
EOF

systemctl enable nadakki
systemctl start nadakki

# Nginx reverse proxy
cat > /etc/nginx/sites-available/nadakki << 'EOF'
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

ln -s /etc/nginx/sites-available/nadakki /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# SSL
certbot --nginx -d your-domain.com
```

---

## 5. WordPress Integration

### wp-config.php
```php
define('NADAKKI_API_URL', 'https://your-api-domain.com');
define('NADAKKI_API_KEY', 'your-api-key');
```

### PHP Client Example
```php
function nadakki_api_call($endpoint, $data = null) {
    $url = NADAKKI_API_URL . $endpoint;
    $args = [
        'headers' => [
            'Content-Type' => 'application/json',
            'Authorization' => 'Bearer ' . NADAKKI_API_KEY,
        ],
        'timeout' => 30,
    ];
    
    if ($data) {
        $args['body'] = json_encode($data);
        $response = wp_remote_post($url, $args);
    } else {
        $response = wp_remote_get($url, $args);
    }
    
    return json_decode(wp_remote_retrieve_body($response), true);
}

// Example: Get dashboard data
$dashboard = nadakki_api_call('/api/v1/dashboard/bank01');

// Example: Run optimization
$result = nadakki_api_call('/api/v1/orchestrator/request', [
    'tenant_id' => 'bank01',
    'request_type' => 'optimize',
    'auto_approve' => true,
]);
```

---

## 6. API Key Authentication (Production)

Add API key middleware in main.py:

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    if api_key != os.getenv("NADAKKI_API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

# Add to endpoints:
@app.post("/api/v1/orchestrator/request", dependencies=[Depends(verify_api_key)])
```

---

## 7. Monitoring

### Health Check
```bash
curl http://localhost:8000/api/v1/system/health
```

### Prometheus Metrics
The TelemetrySidecar exposes Prometheus-compatible metrics:
```
nadakki_operations_total{tenant_id, operation, status}
nadakki_operation_duration_seconds{tenant_id, operation}
nadakki_saga_events_total{tenant_id, status}
nadakki_policy_decisions_total{tenant_id, decision}
```

---

## 8. Adding a New Tenant

```bash
# 1. Store credentials via API
curl -X POST http://localhost:8000/api/v1/tenants/new_bank/credentials \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "your_oauth_refresh_token",
    "customer_id": "1234567890",
    "manager_customer_id": "9876543210"
  }'

# 2. Verify connectivity
curl http://localhost:8000/api/v1/tenants/new_bank/health

# 3. Run initial optimization
curl -X POST http://localhost:8000/api/v1/orchestrator/request \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "new_bank",
    "request_type": "optimize",
    "auto_approve": true
  }'
```

---

## 9. Adding a New Financial Institution (Multi-Tenant)

### Step 1: Onboard Tenant
```bash
POST /api/v1/tenants/{tenant_id}/credentials
```

### Step 2: Add Industry-Specific Knowledge (Optional)
Create files in `knowledge/industry/{vertical}/` to override global defaults:
```
knowledge/
  industry/
    insurance/
      benchmarks.yaml    # Insurance-specific benchmarks
      guardrails.yaml    # Insurance-specific compliance rules
```

### Step 3: Add Tenant-Specific Knowledge (Optional)
```
knowledge/
  {tenant_id}/
    google_ads/
      rules.yaml         # Tenant-specific rules
      guardrails.yaml    # Tenant-specific compliance
```

### Step 4: Set Up Scheduled Workflows
Use the orchestrator schedule endpoint from your cron/Lambda:
```bash
curl -X POST http://localhost:8000/api/v1/orchestrator/schedule \
  -d '{"tenant_id": "new_bank", "trigger": "weekly_optimization"}'
```

---

## Requirements Summary

### Python Packages
```
fastapi>=0.104.0
uvicorn>=0.24.0
pyyaml>=6.0
google-ads>=24.0.0
pydantic>=2.0
aiofiles>=23.0
```

### Optional (Production)
```
gunicorn>=21.2.0         # WSGI server
mangum>=0.17.0           # Lambda adapter
psycopg2-binary>=2.9.0   # PostgreSQL
prometheus-client>=0.19   # Metrics export
```
