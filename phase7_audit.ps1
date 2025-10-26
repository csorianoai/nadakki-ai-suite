# ============================================================
# NADAKKI AI SUITE – PHASE 7 AUDIT SCRIPT (FINAL UTF-8 SAFE)
# ============================================================

$base   = "C:\Users\cesar\Projects\nadakki-ai-suite\nadakki-ai-suite"
$fecha  = Get-Date -Format "yyyyMMdd_HHmmss"
$logDir = "$base\logs"
$log    = "$logDir\phase7_audit_$fecha.log"

# Crear carpeta logs si no existe
if (!(Test-Path $logDir)) { New-Item -Path $logDir -ItemType Directory | Out-Null }

Write-Host ""
Write-Host "=== INICIANDO AUDITORIA DE FACTURACION NADAKKI AI SUITE ===" -ForegroundColor Cyan
Write-Host "(Verificando conexion con backend...)" -ForegroundColor Yellow
Write-Host ""

# ------------------------------------------------------------
# 1. Verificar conexion con el backend
# ------------------------------------------------------------
try {
    $health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method GET -TimeoutSec 4
    Write-Host ("Servidor FastAPI activo: " + $health.status) -ForegroundColor Green
}
catch {
    Write-Host "No se pudo conectar al backend (FastAPI no activo)." -ForegroundColor Red
    Write-Host "Inicia el backend con:" -ForegroundColor Yellow
    Write-Host "   python -m uvicorn main:app --reload --port 8000" -ForegroundColor White
    exit
}

# ------------------------------------------------------------
# 2. Ejecutar auditoria de facturacion
# ------------------------------------------------------------
try {
    Write-Host ""
    Write-Host "Ejecutando auditoria de facturacion..." -ForegroundColor Cyan

    $summary = Invoke-RestMethod -Uri "http://127.0.0.1:8000/billing/summary" -Method GET -TimeoutSec 10

    if ($summary) {
        # Guardar salida JSON con formato
        $summary | ConvertTo-Json -Depth 5 | Out-File $log -Encoding utf8

        Write-Host ""
        Write-Host "=== AUDITORIA COMPLETA ===" -ForegroundColor Green
        Write-Host ("Fecha/Hora: " + (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")) -ForegroundColor Yellow
        Write-Host ("Total Facturado (USD): " + $summary.total_billed_usd) -ForegroundColor Green
        Write-Host ("Transacciones: " + $summary.transactions) -ForegroundColor Cyan
        Write-Host ("Planes activos: " + ($summary.plan_distribution | ConvertTo-Json -Compress)) -ForegroundColor Magenta
        Write-Host ""
        Write-Host ("Archivo de log: " + $log) -ForegroundColor White
    }
    else {
        Write-Host "No se recibieron datos del servidor (/billing/summary sin respuesta)." -ForegroundColor Yellow
    }
}
catch {
    Write-Host ""
    Write-Host "ERROR: No se pudo completar la auditoria." -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor White
}

Write-Host ""
Write-Host "=== AUDITORIA FINALIZADA ===" -ForegroundColor Cyan
