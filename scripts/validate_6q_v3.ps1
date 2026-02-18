param(
  [string]$ProdBaseUrl = "https://nadakki-ai-suite.onrender.com",
  [int]$TimeoutSec = 20
)

$ErrorActionPreference = "Stop"
$stamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$repoPath = (Get-Location).Path
$reportDir = Join-Path $repoPath "logs\daily"
New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
$reportPath = Join-Path $reportDir ("VALIDATION_6Q_{0}.md" -f $stamp)

# ---------- helpers ----------
$Amp = [char]38   # ampersand (&) without using '&' literal
$md = New-Object System.Collections.Generic.List[string]

function L($s){ $md.Add([string]$s) | Out-Null }
function H1($s){ L ("# {0}`n" -f $s) }
function H2($s){ L ("## {0}`n" -f $s) }
function H3($s){ L ("### {0}`n" -f $s) }
function KV($k,$v){ L ("- **{0}**: {1}" -f $k,$v) }
function OK($s){ L ("✅ {0}" -f $s) }
function XX($s){ L ("❌ {0}" -f $s) }
function WW($s){ L ("⚠️ {0}" -f $s) }

function Code($lang,$txt){
  L ("```{0}" -f $lang)
  L $txt
  L "```"
  L ""
}

function Clip([string]$s, [int]$n=500){
  if(-not $s){ return "" }
  if($s.Length -le $n){ return $s }
  return ($s.Substring(0,$n) + "...")
}

function JoinUrl([string]$base,[string]$path){
  return ($base.TrimEnd("/") + "/" + $path.TrimStart("/"))
}

function BuildQueryUrl([string]$base,[string]$path,[hashtable]$qs){
  $pairs = @()
  foreach($k in $qs.Keys){
    $pairs += ("{0}={1}" -f [uri]::EscapeDataString($k), [uri]::EscapeDataString([string]$qs[$k]))
  }
  $q = ($pairs -join $Amp)
  return ("{0}?{1}" -f (JoinUrl $base $path), $q)
}

function GetHttp([string]$url, [hashtable]$headers=@{}){
  try{
    $resp = Invoke-WebRequest -UseBasicParsing -Uri $url -Headers $headers -TimeoutSec $TimeoutSec -Method GET
    return [pscustomobject]@{ ok=$true; status=$resp.StatusCode; body=$resp.Content }
  } catch {
    $e = $_.Exception
    $status = $null
    if ($e.Response -and $e.Response.StatusCode) { $status = [int]$e.Response.StatusCode }
    $body = ""
    try{
      if ($e.Response -and $e.Response.GetResponseStream()){
        $sr = New-Object IO.StreamReader($e.Response.GetResponseStream())
        $body = $sr.ReadToEnd()
      }
    } catch {}
    return [pscustomobject]@{ ok=$false; status=$status; body=$body }
  }
}

function PostJson([string]$url, [string]$json, [hashtable]$headers=@{}){
  try{
    $h = @{"Content-Type"="application/json"}
    foreach($k in $headers.Keys){ $h[$k] = $headers[$k] }
    $resp = Invoke-WebRequest -UseBasicParsing -Uri $url -Headers $h -TimeoutSec $TimeoutSec -Method POST -Body $json
    return [pscustomobject]@{ ok=$true; status=$resp.StatusCode; body=$resp.Content }
  } catch {
    $e = $_.Exception
    $status = $null
    if ($e.Response -and $e.Response.StatusCode) { $status = [int]$e.Response.StatusCode }
    $body = ""
    try{
      if ($e.Response -and $e.Response.GetResponseStream()){
        $sr = New-Object IO.StreamReader($e.Response.GetResponseStream())
        $body = $sr.ReadToEnd()
      }
    } catch {}
    return [pscustomobject]@{ ok=$false; status=$status; body=$body }
  }
}

# ---------- report ----------
H1 ("NADAKKI — Validación 6 Preguntas (v3) — {0}" -f $stamp)
KV "ProdBaseUrl" $ProdBaseUrl
KV "RepoPath" $repoPath
L ""

# Q1/Q2
H2 "Q1/Q2 — Endpoints base y catalogo"
$health = GetHttp (JoinUrl $ProdBaseUrl "/health")
KV "GET /health" $health.status

$catalogUrl = BuildQueryUrl $ProdBaseUrl "/api/catalog" @{ module="marketing"; limit="300" }
$catalog = GetHttp $catalogUrl
KV ("GET /api/catalog?module=marketing{0}limit=300" -f $Amp) $catalog.status

if($catalog.status -eq 200){ OK "Catalogo confirmado en /api/catalog" } else { XX "Catalogo NO responde 200" }
H3 "Catalog sample (first 500 chars)"
Code "json" (Clip $catalog.body 500)
L ""

# Parse catalog
$catalogObj = $null
try { $catalogObj = $catalog.body | ConvertFrom-Json } catch { WW "No pude parsear el JSON del catalogo." }

# Q3
H2 "Q3 — Validacion ejecucion (POST dry_run)"
if(-not $catalogObj){
  WW "Saltando Q3: no hay catalogo parseado."
} else {
  $agents = $catalogObj.agents
  if(-not $agents){ $agents = $catalogObj }

  $execAgents = @($agents | Where-Object { $_.action_methods -and ($_.action_methods -contains "execute") })
  KV "Ejecutables detectados" $execAgents.Count

  if($execAgents.Count -lt 1){
    XX "No encontre agentes ejecutables (action_methods contiene 'execute')."
  } else {
    $a = $execAgents | Select-Object -First 1
    $longId = [string]$a.agent_id
    $shortId = $longId
    if($longId -match "__"){ $shortId = ($longId -split "__")[-1] }

    KV "Agent long_id" $longId
    KV "Agent short_id guess" $shortId

    $payload = '{"payload":{},"dry_run":true}'
    $cands = @(
      "/api/v1/agents/$longId/execute",
      "/api/v1/agents/$shortId/execute",
      "/agents/$longId/execute",
      "/agents/$shortId/execute"
    )

    foreach($p in $cands){
      $url = JoinUrl $ProdBaseUrl $p
      $r = PostJson $url $payload @{}
      L ("- POST {0} -> **{1}**" -f $p, $r.status)
      if($r.body){ Code "json" (Clip $r.body 400) }
    }
  }
}
L ""

# Q4
H2 "Q4 — Tenant header (prueba segura)"
$target = JoinUrl $ProdBaseUrl "/api/v1/config"
$headersTry = @(
  @{ "X-Tenant-ID"="credicefi" },
  @{ "X-Tenant-ID"="demo" },
  @{ "X-Tenant-ID"="tenant_test" }
)

foreach($h in $headersTry){
  $k = $h.Keys | Select-Object -First 1
  $v = $h[$k]
  $r = GetHttp $target $h
  L ("- GET /api/v1/config con {0}:{1} -> **{2}**" -f $k,$v,$r.status)
  if($r.body){ Code "json" (Clip $r.body 250) }
}
WW "Si body/status no cambia entre tenants, tenant aun no aplica en logica (esperable antes de RLS)."
L ""

# Q5
H2 "Q5 — Shape esperado: /api/ai-studio/agents debe espejar /api/catalog"
if($catalogObj){
  $keys = ($catalogObj | Get-Member -MemberType NoteProperty | Select-Object -ExpandProperty Name) -join ", "
  KV "Top-level keys en /api/catalog" $keys
  OK "Requisito: /api/ai-studio/agents devuelve mismo shape (mismas keys)."
} else {
  WW "No pude leer shape del catalogo para comparar."
}
L ""

# Q6
H2 "Q6 — Smoke tests (solo ejecutables reales)"
if($catalogObj){
  $agents = $catalogObj.agents
  if(-not $agents){ $agents = $catalogObj }
  $execAgents = @($agents | Where-Object { $_.action_methods -and ($_.action_methods -contains "execute") })

  if($execAgents.Count -ge 3){
    $smoke = $execAgents | Select-Object -First 3
    L "| # | agent_id | module | category |"
    L "|---|---------|--------|----------|"
    $i=1
    foreach($s in $smoke){
      L ("| {0} | {1} | {2} | {3} |" -f $i, $s.agent_id, $s.module, $s.category)
      $i++
    }
    OK "Smoke list generado desde el catalogo real."
  } else {
    WW "Menos de 3 ejecutables detectados; no puedo proponer 3 smoke desde catalogo."
  }
} else {
  WW "Saltando Q6: no hay catalogo parseado."
}

L ""
H2 "Conclusion"
L "- Reporte sin uso literal del caracter ampersand."
L "- No toca secretos y solo hace dry_run."
L ""

$md -join "`n" | Set-Content -Encoding UTF8 $reportPath
Write-Host "`n✅ Reporte generado: $reportPath`n"
Write-Host ("Abrir con: notepad {0}" -f $reportPath)
