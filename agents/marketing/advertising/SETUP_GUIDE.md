# ═══════════════════════════════════════════════════════════════════════════════
# NADAKKI Google Ads MVP - Setup Guide (Windows)
# ═══════════════════════════════════════════════════════════════════════════════

## QUICK START (PowerShell)

### Step 1: Navigate to your project folder
```powershell
cd C:\Users\cesar\Projects\nadakki-ai-suite\nadakki-ai-suite
```

### Step 2: Extract the ZIP
After downloading `nadakki-google-ads-mvp.zip`, extract it:
```powershell
Expand-Archive -Path nadakki-google-ads-mvp.zip -DestinationPath . -Force
```

### Step 3: Create virtual environment & install dependencies
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r nadakki-google-ads-mvp\requirements.txt
```

### Step 4: Run the standalone test
```powershell
cd nadakki-google-ads-mvp
python main.py
```

Expected output:
```
============================================================
STANDALONE TEST - Day 1 Components
============================================================
1. Storing test credentials for 'bank01'...
   ✓ Credentials stored
2. Retrieving credentials...
   ✓ customer_id: 1234567890
...
ALL DAY 1 TESTS PASSED ✓
============================================================
```

### Step 5: Run the FastAPI server
```powershell
uvicorn main:app --reload --port 8000
```

Then open: http://localhost:8000/health

### Step 6: Test with curl or browser
```powershell
# Health check
Invoke-RestMethod http://localhost:8000/health | ConvertTo-Json

# List operations
Invoke-RestMethod http://localhost:8000/api/v1/operations | ConvertTo-Json

# Store test credentials
$body = @{
    refresh_token = "test_token"
    customer_id = "1234567890"
} | ConvertTo-Json
Invoke-RestMethod -Method POST -Uri http://localhost:8000/api/v1/tenants/bank01/credentials -Body $body -ContentType "application/json"

# Execute operation
$body = @{
    tenant_id = "bank01"
    operation_name = "get_campaign_metrics@v1"
    payload = @{}
} | ConvertTo-Json
Invoke-RestMethod -Method POST -Uri http://localhost:8000/api/v1/operations/execute -Body $body -ContentType "application/json" | ConvertTo-Json
```

## IMPORTANT NOTES

- DO NOT paste Python code directly into PowerShell. Always run files with `python filename.py`
- The project uses InMemoryDatabase by default (no PostgreSQL needed for testing)
- Set `DATABASE_URL` env var to connect to PostgreSQL in production
- Set `CREDENTIAL_ENCRYPTION_KEY` env var for production encryption

## FILE STRUCTURE
```
nadakki-google-ads-mvp/
├── main.py                           # FastAPI app + standalone test
├── requirements.txt                  # Python dependencies
├── core/
│   ├── database.py                   # DB abstraction (PG + InMemory)
│   ├── security/
│   │   └── tenant_vault.py           # Encrypted credential storage
│   ├── google_ads/
│   │   └── client_factory.py         # Client pool per tenant
│   ├── operations/
│   │   └── registry.py               # Operation registry + 2 built-in ops
│   └── reliability/
│       └── idempotency.py            # Deduplication store
├── agents/marketing/                 # Day 3-4: Agent files
├── config/
│   ├── policies/                     # Day 2: Policy YAML per tenant
│   └── workflows/                    # Day 5-6: Workflow YAML files
├── knowledge/                        # Day 3: Knowledge Base YAML
│   ├── global/google_ads/
│   └── industry/financial_services/
├── tests/                            # Day 7: Integration tests
└── docs/
```
