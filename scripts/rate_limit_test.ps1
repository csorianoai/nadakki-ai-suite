<#
.SYNOPSIS
    Rate-limit test for nadakki-ai-suite backend API.

.DESCRIPTION
    Fires N rapid POST dry_run requests against the execute endpoint
    using the same tenant+IP to trigger the 429 rate limiter.
    Default threshold is 30 req/min per tenant+IP.

.PARAMETER ApiUrl
    Base URL of the API (no trailing slash).

.PARAMETER AgentId
    Agent identifier for execute tests.

.PARAMETER TenantId
    Tenant identifier sent via X-Tenant-ID header.

.PARAMETER Requests
    Number of requests to fire (default 35).

.EXAMPLE
    pwsh ./scripts/rate_limit_test.ps1
    pwsh ./scripts/rate_limit_test.ps1 -Requests 50
    pwsh ./scripts/rate_limit_test.ps1 -ApiUrl http://localhost:8000 -Requests 40
#>

param(
    [string]$ApiUrl   = "https://nadakki-ai-suite.onrender.com",
    [string]$AgentId  = "abtestingia__abtestingagentoperative",
    [string]$TenantId = "tenant_demo",
    [int]$Requests    = 35
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  NADAKKI-AI-SUITE  —  Rate Limit Test" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  API URL   : $ApiUrl"
Write-Host "  Agent     : $AgentId"
Write-Host "  Tenant    : $TenantId"
Write-Host "  Requests  : $Requests"
Write-Host "  Time      : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

$execUrl = "$ApiUrl/api/v1/agents/$AgentId/execute"

# Counters
$codes = @{}
$sample429Body = $null
$firstHit429   = $null

Write-Host "Firing $Requests requests..." -ForegroundColor Yellow
Write-Host ""

for ($i = 1; $i -le $Requests; $i++) {
    try {
        $raw = curl.exe -s -w "`n%{http_code}" -X POST $execUrl `
            -H "Content-Type: application/json" `
            -H "X-Tenant-ID: $TenantId" `
            --data-raw '{"payload":{},"dry_run":true}' 2>&1

        $lines = $raw -split "`n"
        $code  = $lines[-1].Trim()
        $body  = ($lines[0..($lines.Length - 2)] -join "`n")

        # Tally
        if ($codes.ContainsKey($code)) { $codes[$code]++ } else { $codes[$code] = 1 }

        # Capture first 429
        if ($code -eq "429" -and -not $sample429Body) {
            $sample429Body = $body
            $firstHit429   = $i
        }

        # Progress indicator
        $color = switch ($code) {
            "200" { "Green" }
            "429" { "Red"   }
            default { "Yellow" }
        }
        Write-Host "  [$i/$Requests] HTTP $code" -ForegroundColor $color
    } catch {
        $errKey = "ERR"
        if ($codes.ContainsKey($errKey)) { $codes[$errKey]++ } else { $codes[$errKey] = 1 }
        Write-Host "  [$i/$Requests] ERROR: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# ── Summary ──────────────────────────────────────────────────────────
Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  RESULTS" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

$codeTable = $codes.GetEnumerator() | Sort-Object Name |
    ForEach-Object { [PSCustomObject]@{ HTTP_Code = $_.Name; Count = $_.Value } }
$codeTable | Format-Table -AutoSize

$got429 = $codes.ContainsKey("429") -and $codes["429"] -ge 1

if ($got429) {
    Write-Host "  [PASS] Rate limiter triggered (first 429 at request #$firstHit429)" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Sample 429 response:" -ForegroundColor Gray
    Write-Host "  $sample429Body" -ForegroundColor Gray
} else {
    Write-Host "  [WARN] No 429 received in $Requests requests." -ForegroundColor Yellow
    Write-Host "         The rate limit threshold may be higher than $Requests req/min," -ForegroundColor Yellow
    Write-Host "         or rate limiting may not be active for this endpoint." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan

if ($got429) { exit 0 } else { exit 1 }
