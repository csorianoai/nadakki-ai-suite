<#
.SYNOPSIS
    Smoke tests for nadakki-ai-suite backend API.

.DESCRIPTION
    Runs health, dry_run execute, audit log, and live gate checks
    against the nadakki-ai-suite API (default: Render deployment).

.PARAMETER ApiUrl
    Base URL of the API (no trailing slash).

.PARAMETER AgentId
    Agent identifier for execute tests.

.PARAMETER TenantId
    Tenant identifier sent via X-Tenant-ID header.

.EXAMPLE
    pwsh ./scripts/smoke.ps1
    pwsh ./scripts/smoke.ps1 -TenantId tenant_demo
    pwsh ./scripts/smoke.ps1 -ApiUrl http://localhost:8000
#>

param(
    [string]$ApiUrl   = "https://nadakki-ai-suite.onrender.com",
    [string]$AgentId  = "abtestingia__abtestingagentoperative",
    [string]$TenantId = "tenant_demo"
)

# ── Helpers ──────────────────────────────────────────────────────────
$ErrorActionPreference = "Stop"
$pass = 0; $fail = 0; $results = @()

function Write-Result {
    param([string]$Name, [bool]$Ok, [string]$Detail)
    if ($Ok) {
        Write-Host "  [PASS] $Name" -ForegroundColor Green
        $script:pass++
    } else {
        Write-Host "  [FAIL] $Name" -ForegroundColor Red
        $script:fail++
    }
    if ($Detail) { Write-Host "         $Detail" -ForegroundColor Gray }
    $script:results += [PSCustomObject]@{ Test = $Name; Result = if ($Ok) { "PASS" } else { "FAIL" }; Detail = $Detail }
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  NADAKKI-AI-SUITE  —  Smoke Tests" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  API URL  : $ApiUrl"
Write-Host "  Agent    : $AgentId"
Write-Host "  Tenant   : $TenantId"
Write-Host "  Time     : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# ── A) Health check ──────────────────────────────────────────────────
Write-Host "[A] Health check  GET /api/v1/health" -ForegroundColor Yellow
try {
    $healthRaw = curl.exe -s -w "`n%{http_code}" "$ApiUrl/api/v1/health" 2>&1
    $healthLines = $healthRaw -split "`n"
    $healthCode  = [int]($healthLines[-1].Trim())
    $healthBody  = ($healthLines[0..($healthLines.Length - 2)] -join "`n")
    $healthOk    = $healthCode -eq 200
    Write-Result "Health endpoint returns 200" $healthOk "HTTP $healthCode"
    if ($healthOk) {
        $healthJson = $healthBody | ConvertFrom-Json
        Write-Host "         version=$($healthJson.version)  agents=$($healthJson.agents_total)" -ForegroundColor Gray
    }
} catch {
    Write-Result "Health endpoint returns 200" $false $_.Exception.Message
}

# ── B) Dry-run execute ───────────────────────────────────────────────
Write-Host ""
Write-Host "[B] Dry-run execute  POST /api/v1/agents/$AgentId/execute" -ForegroundColor Yellow
try {
    $execUrl  = "$ApiUrl/api/v1/agents/$AgentId/execute"
    $execRaw  = curl.exe -s -w "`n%{http_code}" -X POST $execUrl `
        -H "Content-Type: application/json" `
        -H "X-Tenant-ID: $TenantId" `
        --data-raw '{"payload":{},"dry_run":true}' 2>&1
    $execLines = $execRaw -split "`n"
    $execCode  = [int]($execLines[-1].Trim())
    $execBody  = ($execLines[0..($execLines.Length - 2)] -join "`n")
    $execOk    = $execCode -eq 200
    Write-Result "Dry-run returns 200" $execOk "HTTP $execCode"

    if ($execOk) {
        $execJson   = $execBody | ConvertFrom-Json
        $hasTraceId = [bool]$execJson.trace_id
        Write-Result "Response contains trace_id" $hasTraceId "trace_id=$($execJson.trace_id)"
    } else {
        Write-Result "Response contains trace_id" $false "Skipped (non-200)"
    }
} catch {
    Write-Result "Dry-run returns 200" $false $_.Exception.Message
    Write-Result "Response contains trace_id" $false "Skipped"
}

# ── C) Audit logs ────────────────────────────────────────────────────
Write-Host ""
Write-Host "[C] Audit logs  GET /api/v1/audit/logs" -ForegroundColor Yellow
try {
    $auditUrl = "$ApiUrl/api/v1/audit/logs?tenant_id=$TenantId&limit=5"
    $auditRaw = curl.exe -s -w "`n%{http_code}" $auditUrl 2>&1
    $auditLines = $auditRaw -split "`n"
    $auditCode  = [int]($auditLines[-1].Trim())
    $auditBody  = ($auditLines[0..($auditLines.Length - 2)] -join "`n")
    $auditOk    = $auditCode -eq 200
    Write-Result "Audit endpoint returns 200" $auditOk "HTTP $auditCode"

    if ($auditOk) {
        $auditJson = $auditBody | ConvertFrom-Json
        $countOk   = $auditJson.count -ge 1
        Write-Result "Audit count >= 1 (after dry-run)" $countOk "count=$($auditJson.count)"
    } else {
        Write-Result "Audit count >= 1 (after dry-run)" $false "Skipped (non-200)"
    }
} catch {
    Write-Result "Audit endpoint returns 200" $false $_.Exception.Message
    Write-Result "Audit count >= 1 (after dry-run)" $false "Skipped"
}

# ── D) Live gate (403 expected) ──────────────────────────────────────
Write-Host ""
Write-Host "[D] Live gate  POST execute dry_run=false (expect 403)" -ForegroundColor Yellow
try {
    $liveUrl = "$ApiUrl/api/v1/agents/$AgentId/execute"
    $liveRaw = curl.exe -s -w "`n%{http_code}" -X POST $liveUrl `
        -H "Content-Type: application/json" `
        -H "X-Tenant-ID: $TenantId" `
        -H "X-Role: admin" `
        --data-raw '{"payload":{},"dry_run":false}' 2>&1
    $liveLines = $liveRaw -split "`n"
    $liveCode  = [int]($liveLines[-1].Trim())
    $liveBody  = ($liveLines[0..($liveLines.Length - 2)] -join "`n")
    $liveOk    = $liveCode -eq 403
    Write-Result "Live gate returns 403" $liveOk "HTTP $liveCode"

    if ($liveBody) {
        $liveJson = $liveBody | ConvertFrom-Json -ErrorAction SilentlyContinue
        if ($liveJson.detail) {
            Write-Host "         detail: $($liveJson.detail)" -ForegroundColor Gray
        }
    }
} catch {
    Write-Result "Live gate returns 403" $false $_.Exception.Message
}

# ── Summary ──────────────────────────────────────────────────────────
Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  SUMMARY" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Total : $($pass + $fail)" -ForegroundColor White
Write-Host "  Pass  : $pass" -ForegroundColor Green
Write-Host "  Fail  : $fail" -ForegroundColor $(if ($fail -gt 0) { "Red" } else { "Green" })
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

$results | Format-Table -AutoSize

if ($fail -gt 0) {
    Write-Host "Some tests FAILED." -ForegroundColor Red
    exit 1
} else {
    Write-Host "All tests PASSED." -ForegroundColor Green
    exit 0
}
