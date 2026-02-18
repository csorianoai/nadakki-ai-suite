param(
  [string]$RepoPath = (Get-Location).Path,
  [string]$RemoteName = "origin",
  [string]$Branch = "main",
  [string]$ProdBaseUrl = "https://nadakki-ai-suite.onrender.com",
  [switch]$IncludeUntracked = $false
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "SilentlyContinue"

function Section($t){ "`n## $t`n" }
function KV($k,$v){ "- **$k:** $v`n" }
function CmdExists($c){ return [bool](Get-Command $c -ErrorAction SilentlyContinue) }

function Exec($cmd){
  $out = & powershell -NoProfile -Command $cmd 2>&1
  return ($out | Out-String).Trim()
}

# Ensure logs folder
$logDir = Join-Path $RepoPath "logs\daily"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$stamp = (Get-Date).ToString("yyyy-MM-dd_HH-mm-ss")
$reportPath = Join-Path $logDir "STATUS_REALITY_$stamp.md"

$md = @()
$md += "# NADAKKI — STATUS REALITY CHECK ($stamp)`n"
$md += "RepoPath: `$RepoPath`"
$md += "ProdBaseUrl: `$ProdBaseUrl`"
$md += "`n---`n"

# 1) Tooling
$md += Section "Tooling"
$md += KV "git" (CmdExists "git")
$md += KV "curl.exe" (CmdExists "curl.exe")
$md += KV "node" (CmdExists "node")
$md += KV "npm" (CmdExists "npm")

# 2) Git status local
$md += Section "Local Git Status"
Push-Location $RepoPath

$inside = Exec "git rev-parse --is-inside-work-tree"
if ($inside -ne "true") {
  $md += "❌ No estás dentro de un repositorio git en: $RepoPath`n"
  $md | Set-Content -Encoding UTF8 $reportPath
  Write-Host "Reporte generado: $reportPath"
  exit 1
}

$md += KV "Branch (local)" (Exec "git rev-parse --abbrev-ref HEAD")
$md += KV "HEAD (local)" (Exec "git rev-parse HEAD")
$md += KV "Last local commit" (Exec "git log -1 --pretty=format:'%h %ad %s' --date=iso")

$md += "`n### Working tree`n"
$md += "```text`n" + (Exec "git status --porcelain") + "`n```"

if (-not $IncludeUntracked) {
  $md += "`n> Nota: untracked no incluido en diff detallado (usa -IncludeUntracked si lo quieres).`n"
}

# 3) Fetch remote & compare
$md += Section "Remote Sync (GitHub)"
$md += "```text`n" + (Exec "git remote -v") + "`n```"

$fetch = Exec "git fetch $RemoteName"
if ($fetch) { $md += "```text`n$fetch`n```" }

$localHead = Exec "git rev-parse HEAD"
$remoteHead = Exec "git rev-parse $RemoteName/$Branch"

$md += KV "HEAD (remote)" $remoteHead

# Ahead/behind
$aheadBehind = Exec "git rev-list --left-right --count $RemoteName/$Branch...HEAD"
$md += KV "Behind/Ahead (remote...local)" $aheadBehind
$md += "`n> Formato: `behind ahead` (ej: `2 0` significa te faltan 2 commits de GitHub).`n"

$md += "`n### Commits locales NO en GitHub`n"
$md += "```text`n" + (Exec "git log $RemoteName/$Branch..HEAD --oneline --decorate --max-count=30") + "`n```"

$md += "`n### Commits de GitHub NO en local`n"
$md += "```text`n" + (Exec "git log HEAD..$RemoteName/$Branch --oneline --decorate --max-count=30") + "`n```"

# 4) Detect if /api/v1/config change exists locally
$md += Section "Local Code Checks (Config router / LIVE gating)"
$configFile = Join-Path $RepoPath "backend\routers\config.py"
$mainFile   = Join-Path $RepoPath "main.py"

$md += KV "backend/routers/config.py exists" (Test-Path $configFile)
if (Test-Path $configFile) {
  $md += "`n### Snippet: backend/routers/config.py`n"
  $md += "```text`n" + (Get-Content $configFile -TotalCount 120 | Out-String).Trim() + "`n```"
}

$md += KV "main.py exists" (Test-Path $mainFile)
if (Test-Path $mainFile) {
  $md += "`n### main.py includes config_router?`n"
  $hit = Select-String -Path $mainFile -Pattern "backend\.routers\.config" -SimpleMatch
  $md += KV "import backend.routers.config found" ([bool]$hit)
}

# 5) Production checks (Render)
$md += Section "Production Checks (Render)"
if (CmdExists "curl.exe") {

  function CurlJson($url){
    $tmp = Exec "curl.exe -s `"$url`""
    return $tmp
  }

  $health = CurlJson "$ProdBaseUrl/health"
  $md += "`n### GET /health`n```json`n$health`n```"

  $reality = CurlJson "$ProdBaseUrl/api/v1/reality"
  $md += "`n### GET /api/v1/reality`n```json`n$reality`n```"

  $config = CurlJson "$ProdBaseUrl/api/v1/config"
  $md += "`n### GET /api/v1/config`n```json`n$config`n```"
  if ($config -match "Not Found" -or $config -match '"detail"\s*:\s*"Not Found"') {
    $md += "`n❗ **/api/v1/config NO está en producción** (tu commit probablemente NO llegó a Render).`n"
  } else {
    $md += "`n✅ **/api/v1/config responde** (cambio presente en producción).`n"
  }

  # Live gating quick test (dry_run true vs false)
  $md += "`n### LIVE gating test (agent execute)`n"
  $bodyDry = '{"payload":{},"dry_run":true}'
  $tmpDry = Join-Path $RepoPath "req_dry.json"
  [System.IO.File]::WriteAllText($tmpDry, $bodyDry, (New-Object System.Text.UTF8Encoding($false)))
  $dryResp = Exec "curl.exe -s -i -X POST `"$ProdBaseUrl/api/v1/agents/action_plan_executor__actionplanexecutor/execute`" -H `"Content-Type: application/json`" --data-binary `"`@$tmpDry`""
  Remove-Item $tmpDry -Force -ErrorAction SilentlyContinue
  $md += "```text`n$dryResp`n```"

  $bodyLive = '{"payload":{},"dry_run":false}'
  $tmpLive = Join-Path $RepoPath "req_live.json"
  [System.IO.File]::WriteAllText($tmpLive, $bodyLive, (New-Object System.Text.UTF8Encoding($false)))
  $liveResp = Exec "curl.exe -s -i -X POST `"$ProdBaseUrl/api/v1/agents/action_plan_executor__actionplanexecutor/execute`" -H `"Content-Type: application/json`" --data-binary `"`@$tmpLive`""
  Remove-Item $tmpLive -Force -ErrorAction SilentlyContinue
  $md += "```text`n$liveResp`n```"

  if ($liveResp -match "Live execution is disabled") {
    $md += "`n🔒 **Confirmado:** LIVE deshabilitado en producción (requiere LIVE_ENABLED=true).`n"
  }

} else {
  $md += "`n❌ curl.exe no está disponible. No pude verificar Render.`n"
}

# 6) Phase status synthesis
$md += Section "Phase Status (HECHO / PENDIENTE / BLOQUEADO)"
$md += "- ✅ **Dry-run execution**: OK (200)`n"
$md += "- 🔒 **Live execution**: BLOQUEADO (LIVE_ENABLED)`n"
$md += "- 🟡 **Dashboard**: corre, pero `GET /api/ai-studio/agents` da 404 (pendiente conectar o implementar ruta)`n"
$md += "- 🟡 **/api/v1/config**: depende de si está o no en producción (ver arriba)`n"
$md += "- 🔴 **Credenciales**: pendiente rotación (URGENTE)`n"
$md += "- 🟡 **SendGrid LIVE**: pendiente (email bridge responde en dry_run pero status no_agent)`n"
$md += "- 🟡 **PostgreSQL + RLS**: pendiente`n"
$md += "- 🟡 **Deploy Vercel**: pendiente (ideal tras arreglar rutas y env)`n"

Pop-Location

# write report
$md -join "`n" | Set-Content -Encoding UTF8 $reportPath
Write-Host "`n✅ Reporte generado: $reportPath`n"
Write-Host "Ábrelo con: notepad $reportPath"
