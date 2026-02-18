param(
  [string]$ProdBaseUrl = "https://nadakki-ai-suite.onrender.com",
  [int]$TimeoutSec = 20
)

$ErrorActionPreference = "Stop"
$stamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$repoPath = (Get-Location).Path
$reportDir = Join-Path $repoPath "logs\daily"
New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
$reportPath = Join-Path $reportDir ("VALIDATION_6Q_$stamp.md")

$lines = [System.Collections.Generic.List[string]]::new()
function L($s) { $lines.Add([string]$s) }

function SafeGet([string]$url, [hashtable]$headers = @{}) {
  try {
    $r = Invoke-WebRequest -UseBasicParsing -Uri $url -Headers $headers -TimeoutSec $TimeoutSec -Method GET
    return @{ ok = $true; status = [int]$r.StatusCode; body = $r.Content }
  }
  catch {
    $code = 0
    try { $code = [int]$_.Exception.Response.StatusCode } catch { $code = 0 }
    return @{ ok = $false; status = $code; body = "" }
  }
}

function SafePost([string]$url, [string]$json, [hashtable]$headers = @{}) {
  try {
    $h = @{ "Content-Type" = "application/json" }
    foreach ($k in $headers.Keys) { $h[$k] = $headers[$k] }
    $r = Invoke-WebRequest -UseBasicParsing -Uri $url -Headers $h -TimeoutSec $TimeoutSec -Method POST -Body $json
    return @{ ok = $true; status = [int]$r.StatusCode; body = $r.Content }
  }
  catch {
    $code = 0
    try { $code = [int]$_.Exception.Response.StatusCode } catch { $code = 0 }
    return @{ ok = $false; status = $code; body = "" }
  }
}

Write-Host "NADAKKI - Validacion 6 Preguntas (v5)" -ForegroundColor Cyan
Write-Host "Timestamp: $stamp"
Write-Host ""

L "# NADAKKI - Validacion 6 Preguntas - $stamp"
L ""
L ("- ProdBaseUrl: " + $ProdBaseUrl)
L ("- RepoPath: " + $repoPath)
L ""

# Q1/Q2
Write-Host "== Q1/Q2: Health + Catalogo ==" -ForegroundColor Yellow

$health = SafeGet "$ProdBaseUrl/health"
$hStatus = $health.status
Write-Host ("  GET /health -> " + $hStatus) -ForegroundColor $(if ($health.ok) { "Green" } else { "Red" })
L ("## Q1/Q2 - Endpoints y Catalogo")
L ("- GET /health = " + $hStatus)

$catUrl = $ProdBaseUrl + "/api/catalog?module=marketing" + [char]38 + "limit=300"
$catalog = SafeGet $catUrl
Write-Host ("  GET /api/catalog -> " + $catalog.status) -ForegroundColor $(if ($catalog.ok) { "Green" } else { "Red" })
L ("- GET /api/catalog = " + $catalog.status)

$catObj = $null
$agentList = @()
$execList = @()

if ($catalog.ok -and $catalog.body) {
  try {
    $catObj = $catalog.body | ConvertFrom-Json
    if ($catObj.data -and $catObj.data.agents) {
      $agentList = @($catObj.data.agents)
    }
    elseif ($catObj.agents) {
      $agentList = @($catObj.agents)
    }

    $execList = @($agentList | Where-Object {
      $_.action_methods -and ($_.action_methods -contains "execute")
    })

    Write-Host ("  Total agentes: " + $agentList.Count) -ForegroundColor Green
    Write-Host ("  Con execute(): " + $execList.Count) -ForegroundColor Green
    L ("- Total agentes: " + $agentList.Count)
    L ("- Ejecutables: " + $execList.Count)
  }
  catch {
    Write-Host "  Error parseando catalogo" -ForegroundColor Red
    L "- Error parseando catalogo"
  }
}
L ""

# Q3
Write-Host ""
Write-Host "== Q3: Ejecucion agentes (dry_run) ==" -ForegroundColor Yellow
L "## Q3 - Ejecucion (POST dry_run)"

if ($execList.Count -ge 1) {
  $testAgent = $execList[0]
  $longId = ""
  if ($testAgent.agent_id) { $longId = [string]$testAgent.agent_id }
  elseif ($testAgent.id) { $longId = [string]$testAgent.id }
  
  $shortId = $longId
  if ($longId -match "__") { $shortId = ($longId -split "__")[-1] }

  Write-Host ("  Largo: " + $longId) -ForegroundColor Gray
  Write-Host ("  Corto: " + $shortId) -ForegroundColor Gray
  L ("- ID largo: " + $longId)
  L ("- ID corto: " + $shortId)

  $payload = '{"payload":{},"dry_run":true}'

  $routes = @(
    ("/api/v1/agents/" + $longId + "/execute"),
    ("/api/v1/agents/" + $shortId + "/execute"),
    ("/agents/" + $longId + "/execute"),
    ("/agents/" + $shortId + "/execute")
  )

  foreach ($route in $routes) {
    $url = $ProdBaseUrl + $route
    $r = SafePost $url $payload
    $icon = if ($r.ok) { "[OK]" } else { "[XX]" }
    $color = if ($r.ok) { "Green" } else { "Red" }
    Write-Host ("  " + $icon + " POST " + $route + " -> " + $r.status) -ForegroundColor $color
    L ("- POST " + $route + " = " + $r.status)
  }

  # Also try /agents/execute with body
  $execBody = '{"agent_id":"' + $longId + '","dry_run":true}'
  $rExec = SafePost ($ProdBaseUrl + "/agents/execute") $execBody
  $exIcon = if ($rExec.ok) { "[OK]" } else { "[XX]" }
  $exColor = if ($rExec.ok) { "Green" } else { "Red" }
  Write-Host ("  " + $exIcon + " POST /agents/execute (body agent_id) -> " + $rExec.status) -ForegroundColor $exColor
  L ("- POST /agents/execute (body) = " + $rExec.status)
}
else {
  Write-Host "  No hay agentes ejecutables" -ForegroundColor Red
  L "- No hay agentes ejecutables"
}
L ""

# Q4
Write-Host ""
Write-Host "== Q4: Tenant header ==" -ForegroundColor Yellow
L "## Q4 - Tenant header"

$configUrl = $ProdBaseUrl + "/api/v1/config"
$configBase = SafeGet $configUrl
Write-Host ("  GET /api/v1/config (sin header) -> " + $configBase.status) -ForegroundColor $(if ($configBase.ok) { "Green" } else { "Red" })
L ("- /api/v1/config sin header = " + $configBase.status)

$configTenant = SafeGet $configUrl @{ "X-Tenant-ID" = "credicefi" }
Write-Host ("  GET /api/v1/config (credicefi) -> " + $configTenant.status) -ForegroundColor $(if ($configTenant.ok) { "Green" } else { "Red" })
L ("- /api/v1/config con credicefi = " + $configTenant.status)

$connUrl = $ProdBaseUrl + "/api/social/connections"
$conn = SafeGet $connUrl @{ "X-Tenant-ID" = "credicefi" }
Write-Host ("  GET /api/social/connections -> " + $conn.status) -ForegroundColor $(if ($conn.ok) { "Green" } else { "Red" })
L ("- /api/social/connections = " + $conn.status)

$socialUrl = $ProdBaseUrl + "/api/v1/social/status"
$soc = SafeGet $socialUrl
Write-Host ("  GET /api/v1/social/status -> " + $soc.status) -ForegroundColor $(if ($soc.ok) { "Green" } else { "Red" })
L ("- /api/v1/social/status = " + $soc.status)
L ""

# Q5
Write-Host ""
Write-Host "== Q5: Shape catalogo ==" -ForegroundColor Yellow
L "## Q5 - Shape catalogo"

if ($catObj) {
  $topKeys = ($catObj | Get-Member -MemberType NoteProperty | Select-Object -ExpandProperty Name) -join ", "
  Write-Host ("  Top keys: " + $topKeys) -ForegroundColor Green
  L ("- Top-level keys: " + $topKeys)
  L "- /api/ai-studio/agents debe retornar mismo shape"
}
L ""

# Q6
Write-Host ""
Write-Host "== Q6: Smoke test agents ==" -ForegroundColor Yellow
L "## Q6 - Smoke agents"

if ($execList.Count -ge 3) {
  $smoke3 = $execList | Select-Object -First 3
  L "| # | agent_id | category |"
  L "|---|---------|----------|"
  $i = 1
  foreach ($s in $smoke3) {
    $aid = if ($s.agent_id) { $s.agent_id } else { $s.id }
    $cat = if ($s.category) { $s.category } else { "unknown" }
    Write-Host ("  Smoke " + $i + ": " + $aid) -ForegroundColor Green
    L ("| " + $i + " | " + $aid + " | " + $cat + " |")
    $i++
  }
}
elseif ($execList.Count -ge 1) {
  Write-Host ("  Solo " + $execList.Count + " ejecutable(s)") -ForegroundColor Yellow
}
else {
  Write-Host "  0 ejecutables" -ForegroundColor Red
}
L ""

# REPOS
Write-Host ""
Write-Host "== SEGURIDAD: Repos ==" -ForegroundColor Yellow
L "## Seguridad"

$ghBack = SafeGet "https://api.github.com/repos/csorianoai/nadakki-ai-suite"
$backPrivate = ($ghBack.status -eq 404)
if ($backPrivate) {
  Write-Host "  Backend repo: PRIVADO" -ForegroundColor Green
  L "- Backend repo: PRIVADO"
}
else {
  Write-Host "  Backend repo: PUBLICO" -ForegroundColor Red
  L "- Backend repo: PUBLICO"
}

$ghFront = SafeGet "https://api.github.com/repos/csorianoai/nadakki-dashboard"
$frontPrivate = ($ghFront.status -eq 404)
if ($frontPrivate) {
  Write-Host "  Frontend repo: PRIVADO" -ForegroundColor Green
  L "- Frontend repo: PRIVADO"
}
else {
  Write-Host "  Frontend repo: PUBLICO" -ForegroundColor Red
  L "- Frontend repo: PUBLICO"
}
L ""

# RESUMEN
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RESUMEN GATE A" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

L "## RESUMEN"
L ""

$checks = @(
  @{ name = "Backend health"; pass = $health.ok },
  @{ name = "Catalogo 200"; pass = $catalog.ok },
  @{ name = "Ejecutables > 0"; pass = ($execList.Count -gt 0) },
  @{ name = "/api/v1/config 200"; pass = $configBase.ok },
  @{ name = "/api/social/connections 200"; pass = $conn.ok },
  @{ name = "Backend repo privado"; pass = $backPrivate },
  @{ name = "Frontend repo privado"; pass = $frontPrivate }
)

foreach ($c in $checks) {
  $icon = if ($c.pass) { "PASS" } else { "FAIL" }
  $color = if ($c.pass) { "Green" } else { "Red" }
  Write-Host ("  [" + $icon + "] " + $c.name) -ForegroundColor $color
  L ("- " + $icon + " -- " + $c.name)
}

$passCount = ($checks | Where-Object { $_.pass }).Count
$totalCount = $checks.Count
Write-Host ""
Write-Host ("  Score: " + $passCount + " / " + $totalCount) -ForegroundColor $(if ($passCount -eq $totalCount) { "Green" } else { "Yellow" })
L ""
L ("Score: " + $passCount + " / " + $totalCount)

$lines -join "`n" | Set-Content -Encoding UTF8 $reportPath
Write-Host ""
Write-Host ("Reporte: " + $reportPath) -ForegroundColor Green
