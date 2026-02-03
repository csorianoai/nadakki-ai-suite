param(
  [string]$RepoRoot = (Get-Location).Path,
  [string]$MarketingPath = "agents\marketing",
  [string]$CoreList = "agents\marketing\core_agents.txt"
)

function Get-Text($p){ if(Test-Path $p){ return (Get-Content $p -Raw -ErrorAction SilentlyContinue) } return "" }

$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$absMarketing = Join-Path $RepoRoot $MarketingPath
if(!(Test-Path $absMarketing)){ throw "No existe: $absMarketing" }

# Detectar core: si existe core_agents.txt úsalo (uno por línea). Si no, usa todos los .py menos __init__.py
$coreFiles = @()
if(Test-Path (Join-Path $RepoRoot $CoreList)){
  $names = Get-Content (Join-Path $RepoRoot $CoreList) | Where-Object { $_ -and $_.Trim() -ne "" } | ForEach-Object { $_.Trim() }
  foreach($n in $names){
    $p = Join-Path $absMarketing $n
    if(Test-Path $p){ $coreFiles += (Get-Item $p) }
    else{
      # si dieron solo nombre sin .py
      $p2 = Join-Path $absMarketing ($n + ".py")
      if(Test-Path $p2){ $coreFiles += (Get-Item $p2) }
    }
  }
}else{
  $coreFiles = Get-ChildItem -Path $absMarketing -Filter "*.py" -File | Where-Object { $_.Name -ne "__init__.py" }
}

# Buscar requirements y buscar dependencias típicas
$req = Join-Path $RepoRoot "requirements.txt"
$reqText = Get-Text $req

function HasReq([string]$pattern){
  if(!$reqText){ return $false }
  return ($reqText -match $pattern)
}

# Detectar conectores en el repo (ajusta a tu estructura real)
$connectorHints = @(
  "google_ads", "googleads", "meta", "facebook", "instagram", "graph.facebook.com",
  "nadakki.google_ads", "nadakki.meta", "connectors", "integrations"
)

# Reglas mínimas para “operativo como agencia”
$mustHaveGoogle = @("oauth","refresh_token","client_id","client_secret","developer_token","login_customer_id")
$mustHaveMeta   = @("access_token","graph.facebook.com","act_","business","instagram")

$results = @()

foreach($f in $coreFiles){
  $content = Get-Text $f.FullName

  $classes  = [regex]::Matches($content, '^\s*class\s+([A-Za-z_]\w*)', 'Multiline') | ForEach-Object { $_.Groups[1].Value } | Select-Object -Unique
  $funcs    = [regex]::Matches($content, '^\s*def\s+([A-Za-z_]\w*)\s*\(', 'Multiline') | ForEach-Object { $_.Groups[1].Value } | Select-Object -Unique
  $imports1 = [regex]::Matches($content, '^\s*import\s+([A-Za-z0-9_\.]+)', 'Multiline') | ForEach-Object { $_.Groups[1].Value }
  $imports2 = [regex]::Matches($content, '^\s*from\s+([A-Za-z0-9_\.]+)\s+import', 'Multiline') | ForEach-Object { $_.Groups[1].Value }
  $imports  = ($imports1 + $imports2) | Select-Object -Unique

  $envs1 = [regex]::Matches($content, "os\.getenv\(\s*['""]([^'""]+)['""]\s*\)") | ForEach-Object { $_.Groups[1].Value }
  $envs2 = [regex]::Matches($content, "os\.environ\[\s*['""]([^'""]+)['""]\s*\]") | ForEach-Object { $_.Groups[1].Value }
  $envs  = ($envs1 + $envs2) | Select-Object -Unique

  # Tags por heurística
  $isGoogle = ($content -match 'googleads|GoogleAds|google_ads|adwords|customer_id|login_customer_id')
  $isMeta   = ($content -match 'facebook|meta|instagram|graph\.facebook\.com|facebook_business|Marketing API|MetaAds')

  $mentionsOAuth = ($content -match 'oauth|refresh_token|client_secret|client_id')
  $mentionsHTTP  = ($content -match 'requests\.' -or $content -match 'http' -or $content -match 'graph\.facebook\.com')

  # Entry points típicos (ajusta si tus agentes usan otro contrato)
  $hasEntrypoint = ($funcs -contains "run") -or ($funcs -contains "execute") -or ($funcs -contains "handle") -or ($funcs -contains "main")

  # Checks de dependencias
  $needsGoogleLib = $isGoogle
  $hasGoogleLib   = (HasReq "google-ads|googleads") -or ($imports -match "google\.ads|googleads")
  $needsMetaLib   = $isMeta
  $hasMetaLib     = (HasReq "facebook-business|facebook_business") -or ($imports -match "facebook_business") -or ($content -match "graph\.facebook\.com")

  # Gaps por plataforma
  $gaps = @()

  if(!$hasEntrypoint){ $gaps += "No se detectó entrypoint (run/execute/handle/main) para ejecución estándar." }

  if($isGoogle){
    if(-not $mentionsOAuth){ $gaps += "Google: No se ve OAuth/refresh flow (oauth/refresh_token/client_id/client_secret)." }
    if(-not $hasGoogleLib){ $gaps += "Google: Falta librería (google-ads/googleads) en requirements o imports." }
    # claves esperadas (por texto/envs)
    foreach($k in $mustHaveGoogle){
      if(($content -notmatch $k) -and ($envs -notmatch $k.ToUpper())){
        # no penalizar duro, pero señalar
      }
    }
  }

  if($isMeta){
    if(-not ($content -match 'access_token')){ $gaps += "Meta: No se ve access_token (necesario para Graph API)." }
    if(-not $hasMetaLib -and -not $mentionsHTTP){ $gaps += "Meta: No se ve facebook_business SDK ni llamadas HTTP a Graph API." }
  }

  # “Agencia completa”: propuesta mínima de capacidades
  $cap = @()
  if($content -match 'campaign|adset|ads|creative'){ $cap += "Campañas/Ads" }
  if($content -match 'budget|bid|pacing'){ $cap += "Budget/Bids" }
  if($content -match 'abtest|experiment'){ $cap += "A/B Testing" }
  if($content -match 'audien|segment'){ $cap += "Audiencias/Segmentación" }
  if($content -match 'attribution|mta|mmm'){ $cap += "Attribution/Modelos" }
  if($content -match 'report|metrics|kpi|insight'){ $cap += "Reportes/Métricas" }
  if($content -match 'policy|compliance|approve'){ $cap += "Políticas/Compliance" }
  if($content -match 'orchestr|router|pipeline|queue|celery'){ $cap += "Orquestación" }

  $readiness = 100
  $readiness -= ($gaps.Count * 12)
  if($isGoogle -and !$mentionsOAuth){ $readiness -= 15 }
  if($isGoogle -and !$hasGoogleLib){ $readiness -= 15 }
  if($isMeta -and !($content -match 'access_token')){ $readiness -= 15 }
  if($readiness -lt 0){ $readiness = 0 }

  $results += [pscustomobject]@{
    agent_file    = $f.Name
    path          = $f.FullName.Replace($RepoRoot,".")
    classes       = ($classes -join ", ")
    functions     = ($funcs -join ", ")
    imports_top   = (($imports | Select-Object -First 12) -join ", ")
    env_vars      = ($envs -join ", ")
    tags          = (@(
                      if($isGoogle){"GoogleAds"} 
                      if($isMeta){"Meta(FB/IG)"} 
                      if(!$isGoogle -and !$isMeta){"Generic"}
                    ) -join " | ")
    capabilities  = ($cap -join " | ")
    readiness     = $readiness
    gaps          = ($gaps -join "  |  ")
  }
}

# Salidas
$reportDir = Join-Path $RepoRoot "reports"
New-Item -ItemType Directory -Force -Path $reportDir | Out-Null

$jsonPath = Join-Path $reportDir "marketing_core_audit_$ts.json"
$csvPath  = Join-Path $reportDir "marketing_core_audit_$ts.csv"
$mdPath   = Join-Path $reportDir "marketing_core_audit_$ts.md"

$results | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 $jsonPath
$results | Export-Csv -NoTypeInformation -Encoding UTF8 $csvPath

# Markdown bonito
$top = $results | Sort-Object readiness -Descending
$googleCount = ($results | Where-Object { $_.tags -match "GoogleAds" }).Count
$metaCount   = ($results | Where-Object { $_.tags -match "Meta" }).Count
$avgReady    = [math]::Round(($results | Measure-Object readiness -Average).Average,2)

$md = @()
$md += "# NADAKKI — Marketing Core Audit ($ts)"
$md += ""
$md += "RepoRoot: **$RepoRoot**"
$md += ""
$md += "Total agentes auditados: **$($results.Count)**"
$md += "Google-tagged: **$googleCount** | Meta-tagged: **$metaCount** | Readiness promedio: **$avgReady**"
$md += ""
$md += "## Top 10 por readiness"
$md += ""
$md += "| Agent | Tags | Readiness | Capabilities | Gaps |"
$md += "|---|---:|---:|---|---|"
foreach($r in ($top | Select-Object -First 10)){
  $md += "| $($r.agent_file) | $($r.tags) | $($r.readiness) | $($r.capabilities) | $($r.gaps) |"
}
$md += ""
$md += "## Detalle completo"
$md += ""
$md += "| Agent | Readiness | Tags | Entrypoints/Funcs | Imports (top) | Env Vars |"
$md += "|---|---:|---|---|---|---|"
foreach($r in ($results | Sort-Object readiness -Descending)){
  $md += "| $($r.agent_file) | $($r.readiness) | $($r.tags) | $($r.functions) | $($r.imports_top) | $($r.env_vars) |"
}
$md += ""
$md += "## Reglas mínimas para operar como agencia (checklist general)"
$md += "- Orquestación: router/pipeline + retries + rate-limit + logs + trazabilidad (request_id/tenant_id)"
$md += "- Google Ads: OAuth refresh + developer_token + login_customer_id + cliente/manager + manejo de cuotas"
$md += "- Meta Ads (FB/IG): access_token + app_id/app_secret + ad_account_id (act_) + permisos + Graph API"
$md += "- Creativo: generación + validación de políticas + landing checks"
$md += "- Reporting: pull de métricas, normalización, dashboards/exports"
$md += ""
$md -join "`n" | Set-Content -Encoding UTF8 $mdPath

# Consola (resumen)
Write-Host "`n══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host " NADAKKI — AUDITORÍA CORE MARKETING  ($ts)" -ForegroundColor Cyan
Write-Host "══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Agentes auditados: $($results.Count) | Google-tagged: $googleCount | Meta-tagged: $metaCount | Avg readiness: $avgReady" -ForegroundColor Green
Write-Host "`nTop 10 readiness:" -ForegroundColor Yellow
$top | Select-Object -First 10 agent_file,tags,readiness,capabilities | Format-Table -AutoSize

Write-Host "`nReportes generados:" -ForegroundColor Cyan
Write-Host " - $mdPath" -ForegroundColor Gray
Write-Host " - $jsonPath" -ForegroundColor Gray
Write-Host " - $csvPath" -ForegroundColor Gray

# Señalar “faltantes típicos” del repo
$missing = @()
if(!(Test-Path (Join-Path $RepoRoot ".env"))){ $missing += ".env (credenciales) no existe en la raíz" }
if($reqText -and -not ($reqText -match "requests")){ $missing += "requirements: falta requests (común para Graph API)" }
if($reqText -and -not ($reqText -match "google-ads|googleads") -and $googleCount -gt 0){ $missing += "requirements: falta google-ads/googleads" }
if($reqText -and -not ($reqText -match "facebook-business|facebook_business") -and $metaCount -gt 0){ $missing += "requirements: falta facebook-business SDK (opcional si usan requests)" }

if($missing.Count -gt 0){
  Write-Host "`nFaltantes típicos detectados:" -ForegroundColor Red
  $missing | ForEach-Object { Write-Host " - $_" -ForegroundColor Red }
}

