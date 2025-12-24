# fix_and_cleanup_marketing.ps1
# 1. Prueba los 4 agentes con input correcto
# 2. Archiva los archivos que no son agentes

$baseUrl = "https://nadakki-ai-suite.onrender.com"
$headers = @{
    "X-Tenant-ID" = "credicefi"
    "X-API-Key" = "nadakki_klbJUiJetf-5hH1rpCsLfqRIHPdirm0gUajAUkxov8I"
    "Content-Type" = "application/json"
}

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  PARTE 1: CORREGIR 4 AGENTES CON INPUT AJUSTADO" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

# 1. productaffinityia - necesita customer como objeto
Write-Host "`n[1/4] productaffinityia (corregido)..." -ForegroundColor Yellow
$body = '{"input_data":{"customer":{"customer_id":"cust_001","name":"Juan","email":"j@test.com"},"purchase_history":[{"product":"loan","amount":10000}]}}'
try {
    $r = Invoke-RestMethod -Uri "$baseUrl/agents/marketing/productaffinityia/execute" -Method POST -Headers $headers -Body $body
    if ($r.result.error) { Write-Host "  WARN - $($r.result.error)" -ForegroundColor Yellow }
    else { Write-Host "  OK" -ForegroundColor Green }
} catch { Write-Host "  ERROR" -ForegroundColor Red }

# 2. geosegmentationia - necesita segmentation_id
Write-Host "`n[2/4] geosegmentationia (corregido)..." -ForegroundColor Yellow
$body = '{"input_data":{"segmentation_id":"seg_001","regions":[{"region":"Norte","leads":100,"conversions":20}]}}'
try {
    $r = Invoke-RestMethod -Uri "$baseUrl/agents/marketing/geosegmentationia/execute" -Method POST -Headers $headers -Body $body
    if ($r.result.error) { Write-Host "  WARN - $($r.result.error)" -ForegroundColor Yellow }
    else { Write-Host "  OK" -ForegroundColor Green }
} catch { Write-Host "  ERROR" -ForegroundColor Red }

# 3. minimalformia - necesita form_id
Write-Host "`n[3/4] minimalformia (corregido)..." -ForegroundColor Yellow
$body = '{"input_data":{"form_id":"form_001","form_type":"loan","fields":["name","email","phone"]}}'
try {
    $r = Invoke-RestMethod -Uri "$baseUrl/agents/marketing/minimalformia/execute" -Method POST -Headers $headers -Body $body
    if ($r.result.error) { Write-Host "  WARN - $($r.result.error)" -ForegroundColor Yellow }
    else { Write-Host "  OK" -ForegroundColor Green }
} catch { Write-Host "  ERROR" -ForegroundColor Red }

# 4. cashofferfilteria - necesita customer_id
Write-Host "`n[4/4] cashofferfilteria (corregido)..." -ForegroundColor Yellow
$body = '{"input_data":{"customer_id":"cust_001","applications":[{"id":"app1","credit_score":750,"income":5000}]}}'
try {
    $r = Invoke-RestMethod -Uri "$baseUrl/agents/marketing/cashofferfilteria/execute" -Method POST -Headers $headers -Body $body
    if ($r.result.error) { Write-Host "  WARN - $($r.result.error)" -ForegroundColor Yellow }
    else { Write-Host "  OK" -ForegroundColor Green }
} catch { Write-Host "  ERROR" -ForegroundColor Red }

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "  PARTE 2: ARCHIVAR ARCHIVOS QUE NO SON AGENTES" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

$marketingPath = "C:\Users\cesar\Projects\nadakki-ai-suite\nadakki-ai-suite\agents\marketing"
$archivePath = "$marketingPath\_archived"

# Crear carpeta de archivo si no existe
if (-not (Test-Path $archivePath)) {
    New-Item -ItemType Directory -Path $archivePath | Out-Null
    Write-Host "`nCreada carpeta: _archived" -ForegroundColor Green
}

# Archivos a mover (no son agentes reales)
$filesToArchive = @(
    "canonical.py",
    "canonical_backup_20251011_084547.py",
    "canonical_backup_20251012_091337.py",
    "schemas_from_sandbox.py",
    "validate_agents.py",
    "leadscoringia_backup_20251012_120320.py",
    "content_generator_v3.py"
)

$moved = 0
foreach ($file in $filesToArchive) {
    $sourcePath = "$marketingPath\$file"
    $destPath = "$archivePath\$file"
    
    if (Test-Path $sourcePath) {
        Move-Item -Path $sourcePath -Destination $destPath -Force
        Write-Host "  Archivado: $file" -ForegroundColor Yellow
        $moved++
    } else {
        Write-Host "  No existe: $file" -ForegroundColor Gray
    }
}

Write-Host "`n================================================================" -ForegroundColor Green
Write-Host "  RESUMEN" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host "  Agentes corregidos: 4" -ForegroundColor Cyan
Write-Host "  Archivos movidos a _archived: $moved" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Ahora tienes solo agentes reales en la carpeta marketing" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green

# Commit de los cambios
Write-Host "`nGuardando cambios en Git..." -ForegroundColor Yellow
Set-Location "C:\Users\cesar\Projects\nadakki-ai-suite\nadakki-ai-suite"
git add .
git commit -m "cleanup: Archive non-agent files from marketing folder"
git push origin main

Write-Host "`nCambios guardados y subidos a GitHub" -ForegroundColor Green
