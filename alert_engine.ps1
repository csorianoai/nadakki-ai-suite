# ════════════════════════════════════════════════════════════════
# NADAKKI AI SUITE - ALERT ENGINE v4.0
# Autor: César Soriano
# Fecha: 2025-10-24
# Objetivo: Detectar errores o latencias altas y registrar alertas
# ════════════════════════════════════════════════════════════════

$LogDir = "logs/performance"
$AlertDir = "logs/alerts"
if (-not (Test-Path $AlertDir)) { New-Item -ItemType Directory -Path $AlertDir | Out-Null }

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$AlertFile = "$AlertDir/alert_$Timestamp.log"

Write-Host "`n🚨 Iniciando monitoreo automático Nadakki AI Suite..." -ForegroundColor Cyan

$logs = Get-ChildItem $LogDir -Filter "sla_report_*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 3

foreach ($log in $logs) {
    Write-Host "🔍 Analizando $($log.Name)" -ForegroundColor Yellow
    Get-Content $log.FullName | ForEach-Object {
        if ($_ -match "Status:\s+(?<status>\S+)\s+-\s+(?<latency>\d+)") {
            $status = $matches['status']
            $latency = [int]$matches['latency']
            if ($status -ne "200" -or $latency -gt 3000) {
                $msg = "⚠️ [$($log.Name)] Status=$status | Latency=${latency}ms"
                Add-Content $AlertFile $msg
                Write-Host $msg -ForegroundColor Red
            }
        }
    }
}

if (Test-Path $AlertFile) {
    Write-Host "`n✅ Alertas registradas en: $AlertFile" -ForegroundColor Green
} else {
    Write-Host "`n✅ Sin alertas detectadas (todo estable)" -ForegroundColor Green
}
