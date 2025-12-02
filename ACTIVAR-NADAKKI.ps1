# ==================================================
# ACTIVAR-NADAKKI.ps1 - VERSION CORREGIDA
# ACTIVACIÓN COMPLETA SIN ERRORES
# ==================================================

param([switch]$Force)

$BaseURL = "http://127.0.0.1:8000"
$StartTime = Get-Date
$LogFile = "logs/activation_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

# Crear directorio de logs
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" -Force | Out-Null
}

function Write-Log {
    param([string]$Message, [string]$Color = "White")
    $timestamp = Get-Date -Format "HH:mm:ss"
    $logMessage = "[$timestamp] $Message"
    Write-Host $logMessage -ForegroundColor $Color
    Add-Content -Path $LogFile -Value $logMessage
}

Clear-Host
Write-Host "NADAKKI AI SUITE - ACTIVACION TOTAL v3.4.1" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# ---------- 1. Verificar servidor activo ----------
Write-Log "Verificando servidor FastAPI..." "Yellow"

$serverAlive = $false
try {
    $healthCheck = Invoke-RestMethod -Uri "$BaseURL/" -TimeoutSec 3
    if ($healthCheck.service) { 
        $serverAlive = $true 
        Write-Log "Servidor ya activo" "Green"
    }
} catch {
    # Servidor no responde, verificar procesos
    $runningProcesses = Get-Process -ErrorAction SilentlyContinue | Where-Object {$_.ProcessName -like "*uvicorn*"}
    if ($runningProcesses) {
        Write-Log "Proceso uvicorn ya en ejecucion (PID: $($runningProcesses[0].Id))" "Yellow"
        $serverAlive = $true
    } else {
        Write-Log "Iniciando servidor FastAPI en nueva ventana..." "Yellow"
        
        # Crear script temporal para iniciar servidor
        $serverScript = @"
cd '$PWD'
python -m uvicorn main:app --reload --port 8000
"@
        $tempFile = "start_server_temp.ps1"
        Set-Content -Path $tempFile -Value $serverScript
        
        # Iniciar en nueva ventana
        Start-Process PowerShell -ArgumentList "-NoExit", "-File", $tempFile
        
        # Esperar inicializacion
        Start-Sleep -Seconds 8
        
        # Verificar conexion
        try {
            $healthCheck = Invoke-RestMethod -Uri "$BaseURL/" -TimeoutSec 5
            if ($healthCheck.service) {
                $serverAlive = $true
                Write-Log "Servidor operativo" "Green"
            }
        } catch {
            Write-Log "No se pudo iniciar el servidor" "Red"
        }
        
        # Limpiar archivo temporal
        if (Test-Path $tempFile) {
            Remove-Item $tempFile -Force
        }
    }
}

if (-not $serverAlive) {
    Write-Log "Abortando activacion - servidor no disponible" "Red"
    exit 1
}

# ---------- 2. Ejecutar FASE-9 si es necesario ----------
$fase9Files = Get-ChildItem -Path "logs" -Filter "fase9_execution_*" -ErrorAction SilentlyContinue
$recentExecution = $false

if ($fase9Files) {
    $latestFase9 = $fase9Files | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    $age = (Get-Date) - $latestFase9.LastWriteTime
    
    if ($age.TotalHours -lt 24 -and -not $Force) {
        $recentExecution = $true
        $hoursAgo = [math]::Round($age.TotalHours, 1)
        Write-Log "FASE-9 ya ejecutada hace $hoursAgo horas" "Cyan"
    }
}

if (-not $recentExecution -and (Test-Path "FASE-9-FINAL.ps1")) {
    Write-Log "Ejecutando FASE-9-FINAL.ps1..." "Cyan"
    try {
        & ".\FASE-9-FINAL.ps1"
        Write-Log "FASE-9 completada correctamente" "Green"
    } catch {
        Write-Log "Error ejecutando FASE-9: $($_.Exception.Message)" "Red"
    }
}

# ---------- 3. Verificar componentes del sistema ----------
Write-Log "Verificando componentes del sistema..." "Cyan"

$components = @{
    "Base de datos" = "tenants.db"
    "Dashboards" = "dashboards" 
    "Kit comercial" = "kit_comercial_fase9"
    "Logs" = "logs"
}

foreach ($name in $components.Keys) {
    $path = $components[$name]
    if (Test-Path $path) {
        Write-Log "✅ $name - OK" "Green"
    } else {
        Write-Log "❌ $name - No encontrado" "Red"
    }
}

# ---------- 4. Abrir dashboards y kit comercial ----------
if (Test-Path "dashboards") {
    $htmlFiles = Get-ChildItem "dashboards" -Filter "*.html"
    foreach ($file in $htmlFiles) {
        Write-Log "Abriendo dashboard: $($file.Name)" "White"
        Start-Process $file.FullName
    }
}

if (Test-Path "kit_comercial_fase9") {
    Write-Log "Abriendo kit comercial..." "White"
    Start-Process "kit_comercial_fase9"
}

# ---------- 5. Mostrar acciones comerciales ----------
Write-Log "ACCIONES COMERCIALES INMEDIATAS:" "Cyan"
Write-Log "1. Credicefi - Caso piloto comercial" "White"
Write-Log "2. Coopafer - Demo via Zoom" "White"
Write-Log "3. Prestatu.do - Validacion fintech" "White"

Write-Log "METAS SEMANA 1:" "Yellow"
Write-Log "- 3+ demos ejecutadas" "White"
Write-Log "- 10+ insights de feedback" "White"
Write-Log "- $1K+ MRR (1 piloto firmado)" "White"

# ---------- 6. Resumen final ----------
$endTime = Get-Date
$duration = $endTime - $StartTime

Write-Log "ACTIVACION COMPLETA EN $([math]::Round($duration.TotalMinutes, 1)) minutos" "Green"
Write-Log "Servidor: $BaseURL" "White"
Write-Log "Documentacion: $BaseURL/docs" "White"
Write-Log "Log detallado: $LogFile" "White"

Write-Host "`nSISTEMA LISTO PARA OPERACIONES COMERCIALES" -ForegroundColor Cyan
Write-Host "Mantén abierta la ventana del servidor para uso continuo." -ForegroundColor White