# =========================================================
# NADAKKI AI SUITE ? PRE-PHASE 4 VALIDATION (FINAL FIXED)
# Autor: C?sar Soriano
# Fecha: 2025-10-23
# =========================================================

Write-Host ""
Write-Host "=== INICIANDO VALIDACION PRE?PHASE 4 ===" -ForegroundColor Cyan

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "C:\Backups"
$logDir = "logs\validation"

if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir | Out-Null
}
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}

$logFile = "$logDir\prephase4_validation_$timestamp.log"

# 1) BACKUP COMPLETO
Write-Host "`nCreando backup completo..." -ForegroundColor Yellow
$zipFile = "C:\Backups\nadakki_backup_$timestamp.zip"
Compress-Archive -Path "C:\Users\cesar\Projects\nadakki-ai-suite\nadakki-ai-suite" `
    -DestinationPath $zipFile -Force
Add-Content $logFile "Backup generado: $zipFile"
Write-Host ("Backup completado: {0}" -f $zipFile) -ForegroundColor Green

# 2) VERIFICACION FASTAPI
Write-Host "`nVerificando carga del backend (main.py)..." -ForegroundColor Yellow
try {
    python -c "import importlib; importlib.import_module('main'); print('FASTAPI_OK')" |
        Tee-Object -FilePath $logFile -Append
    Write-Host "FastAPI importado correctamente." -ForegroundColor Green
}
catch {
    Write-Host ("Error al importar FastAPI: {0}" -f $_.Exception.Message) -ForegroundColor Red
    Add-Content $logFile ("Error import main.py: {0}" -f $_.Exception.Message)
}

# 3) CHEQUEO DE ENDPOINTS CRITICOS
Write-Host "`nValidando endpoints criticos..." -ForegroundColor Yellow
$baseURL = "http://127.0.0.1:8000"
$routes = @(
    "/health",
    "/api/v1/wp/agents",
    "/api/v1/wp/evaluate",
    "/api/v1/wp/auth"
)
foreach ($r in $routes) {
    try {
        $res = Invoke-WebRequest -Uri "$baseURL$r" -UseBasicParsing -TimeoutSec 3
        Write-Host ("{0,-40} {1,10}" -f $r, $res.StatusCode) -ForegroundColor Green
        Add-Content $logFile ("{0} -> {1}" -f $r, $res.StatusCode)
    }
    catch {
        Write-Host ("{0,-40} {1,10}" -f $r, "ERROR") -ForegroundColor Red
        Add-Content $logFile ("{0} -> ERROR" -f $r)
    }
}

# 4) VERIFICAR WP INTEGRATION
Write-Host "`nVerificando archivos criticos WordPress..." -ForegroundColor Yellow
$paths = @(
    "C:\Users\cesar\Projects\nadakki-ai-suite\nadakki-ai-suite\includes\nadakki-monitor.php",
    "C:\Users\cesar\Projects\nadakki-ai-suite\nadakki-ai-suite\includes\nadakki-multi-tenant.php"
)
foreach ($p in $paths) {
    if (Test-Path $p) {
        Write-Host ("Archivo presente: {0}" -f $p) -ForegroundColor Green
        Add-Content $logFile ("Archivo encontrado: {0}" -f $p)
    }
    else {
        Write-Host ("Archivo faltante: {0}" -f $p) -ForegroundColor Red
        Add-Content $logFile ("Archivo faltante: {0}" -f $p)
    }
}

# 5) VALIDACION UNITTESTS
Write-Host "`nEjecutando tests automaticos..." -ForegroundColor Yellow
python -m unittest discover tests | Tee-Object -FilePath $logFile -Append

# 6) RESULTADO FINAL
Write-Host "`n=== VALIDACION COMPLETADA ===" -ForegroundColor Green
Write-Host ("Log: {0}" -f $logFile) -ForegroundColor Cyan
Write-Host ("Backup: {0}" -f $zipFile) -ForegroundColor Yellow
