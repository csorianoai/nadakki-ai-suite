# MANUS — BACKEND SMOKE/E2E PACK (Fast, Parallel-safe)

## GOAL (Today)
Automate repeatable validation of:
- health
- execute dry_run
- live gate (403 unless LIVE_ENABLED=true AND role=admin)
- rate limiting (429 after threshold)
- audit logs write/read
No secrets required.

## TASKS

### M1) Create scripts (PowerShell) under scripts/
1) scripts/smoke.ps1
- Runs:
  - GET /api/v1/health (expect 200)
  - POST execute dry_run=true (expect 200 + trace_id)
  - GET audit logs for tenant (expect count>=1)
  - POST dry_run=false with X-Role admin (expect 403 unless LIVE_ENABLED true)
- Must not write to C:\ root; use $PWD temp files or pipeline.

2) scripts/rate_limit_test.ps1
- Fire 35 requests quickly for same tenant/ip key and confirm at least one 429.
- Print summary counts: 200/403/429.

### M2) Add minimal docs
- docs/SMOKE_TESTS.md with:
  - how to run scripts locally
  - how to run against Render
  - expected outputs

### M3) Optional: lightweight CI step (no secrets)
- Add GitHub Action job that runs curl-based health checks (non-blocking or nightly)
- Must not expose secrets.

## DELIVERABLES
- PR merged to main
- scripts created
- docs added
