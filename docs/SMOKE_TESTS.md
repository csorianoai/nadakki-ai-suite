# Backend Smoke & E2E Tests

This document provides instructions for running the backend smoke and end-to-end (E2E) test scripts for the **nadakki-ai-suite**.

These tests are designed to be run from a developer's local machine (Windows) to quickly validate the core functionality of the deployed application.

## Prerequisites

- **Windows PowerShell**: The scripts are written in PowerShell (`.ps1`) and require a modern version of PowerShell to run. This is pre-installed on Windows 10 and 11.
- **curl**: The scripts use `curl.exe` for making HTTP requests. This is included by default in recent versions of Windows.

## Running the Tests

All scripts are located in the `/scripts` directory. Open a PowerShell terminal, navigate to the root of the repository, and execute the scripts as shown below.

### 1. Comprehensive Smoke Test

The `smoke.ps1` script runs a series of checks against the key API endpoints to ensure they are operational and behaving as expected.

**What it tests:**
- `GET /api/v1/health`: Checks if the service is healthy (HTTP 200).
- `POST /api/v1/agents/{AgentId}/execute` (dry_run): Verifies that a dry-run execution completes successfully (HTTP 200) and returns a `trace_id`.
- `GET /api/v1/audit/logs`: Confirms that the dry-run execution was logged in the audit trail.
- `POST /api/v1/agents/{AgentId}/execute` (live): Checks the live gate functionality, ensuring the endpoint returns a `403 Forbidden` error when `LIVE_ENABLED` is false.

**How to run:**

```powershell
# Run with default parameters (targets Render URL)
pwsh .\scripts\smoke.ps1

# Specify a custom Tenant ID
pwsh .\scripts\smoke.ps1 -TenantId my_custom_tenant

# Target a local development server
pwsh .\scripts\smoke.ps1 -ApiUrl http://localhost:8000
```

**Expected Output:**

The script will print a summary table. A successful run looks like this:

```
=============================================
  SUMMARY
=============================================
  Total : 4
  Pass  : 4
  Fail  : 0
=============================================

Test                           Result Detail
----                           ------ ------
Health endpoint returns 200    PASS   HTTP 200
Response contains trace_id     PASS   trace_id=xxxxxxxx
Audit count >= 1               PASS   count=1
Live gate returns 403          PASS   HTTP 403

All tests PASSED.
```

### 2. Rate Limit Test

The `rate_limit_test.ps1` script is designed to verify that the API's rate limiting is functioning correctly. It fires a burst of requests to the execute endpoint to trigger the `429 Too Many Requests` response.

**What it tests:**
- Fires N rapid, identical `dry_run=true` requests.
- The default API rate limit is 30 requests per minute per tenant/IP combination.
- The script expects to receive at least one `HTTP 429` response when sending more than 30 requests.

**How to run:**

```powershell
# Run with default of 35 requests
pwsh .\scripts\rate_limit_test.ps1

# Run with a higher number of requests
pwsh .\scripts\rate_limit_test.ps1 -Requests 50
```

**Expected Output:**

The script will show the status of each request and then provide a summary of the HTTP codes received. A successful test will show at least one 429 response.

```
=============================================
  RESULTS
=============================================

HTTP_Code Count
--------- -----
200       30
429       5

  [PASS] Rate limiter triggered (first 429 at request #31)

  Sample 429 response:
  {"detail":"Rate limit exceeded: 30 per 1 minute"}
```

## Target Environment

By default, both scripts are configured to run against the live production environment hosted on Render:

- **URL**: `https://nadakki-ai-suite.onrender.com`

To target a different environment (e.g., a local instance or a staging server), use the `-ApiUrl` parameter.
