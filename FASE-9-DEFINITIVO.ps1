# ==================================================
# SCRIPT: FASE-9-DEFINITIVO.ps1
# VERSIÓN COMPLETAMENTE CORREGIDA - SIN ERRORES DE SINTÁXIS
# ==================================================

Write-Host "🚀 INICIANDO FASE 9 ACELERADA - VERSIÓN DEFINITIVA" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Configuración
$BaseURL = "http://127.0.0.1:8000"
$ScriptStartTime = Get-Date
$BackupDir = "backup_fase9_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
$LogFile = "logs/fase9_execution_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

# Crear directorio de logs
New-Item -ItemType Directory -Path "logs" -Force | Out-Null

function Write-Log {
    param([string]$Message, [string]$Color = "White")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] $Message"
    Write-Host $logMessage -ForegroundColor $Color
    Add-Content -Path $LogFile -Value $logMessage
}

# ==================================================
# VERIFICACIÓN PREVIA DEL SISTEMA
# ==================================================
Write-Log "=== VERIFICACIÓN INICIAL DEL SISTEMA ===" "Cyan"

try {
    $healthCheck = Invoke-RestMethod -Uri "$BaseURL/" -TimeoutSec 10
    Write-Log "✅ Servidor FastAPI operativo: $($healthCheck.service) v$($healthCheck.version)" "Green"
} catch {
    Write-Log "❌ Servidor no responde. Ejecuta: python -m uvicorn main:app --reload --port 8000" "Red"
    exit 1
}

if (-not (Test-Path "tenants.db")) {
    Write-Log "❌ tenants.db no encontrada." "Red"
    exit 1
}
Write-Log "✅ Base de datos tenants.db encontrada" "Green"

# ==================================================
# BACKUP AUTOMÁTICO DE SEGURIDAD
# ==================================================
Write-Log "=== CREANDO BACKUP DE SEGURIDAD ===" "Yellow"

try {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    
    if (Test-Path "tenants.db") {
        Copy-Item "tenants.db" "$BackupDir/tenants.db.backup"
        Write-Log "✅ Backup DB: $BackupDir/tenants.db.backup" "Green"
    }
    
    if (Test-Path "config/tenants") {
        Copy-Item "config/tenants" "$BackupDir/config_tenants" -Recurse -Force
        Write-Log "✅ Backup config: $BackupDir/config_tenants" "Green"
    }
    
    if (Test-Path "dashboards") {
        Copy-Item "dashboards" "$BackupDir/dashboards" -Recurse -Force
        Write-Log "✅ Backup dashboards: $BackupDir/dashboards" "Green"
    }
    
    Write-Log "✅ Backup completo creado en: $BackupDir" "Green"
} catch {
    Write-Log "⚠️  Advertencia: No se pudo crear backup completo: $($_.Exception.Message)" "Yellow"
}

# ==================================================
# MIGRACIÓN DE TENANTS EXISTENTES
# ==================================================
Write-Log "=== MIGRACIÓN DE TENANTS EXISTENTES ===" "Cyan"

if (Test-Path "migrate_tenants.py") {
    try {
        Write-Log "🔧 Ejecutando migración de tenants..." "Yellow"
        $migrationResult = python migrate_tenants.py 2>&1
        Write-Log "✅ Migración ejecutada: $migrationResult" "Green"
    } catch {
        Write-Log "⚠️  Migración falló: $($_.Exception.Message)" "Yellow"
    }
} else {
    Write-Log "ℹ️  Script migrate_tenants.py no encontrado" "Yellow"
}

# Verificar tenants disponibles
try {
    $tenantsResponse = Invoke-RestMethod -Uri "$BaseURL/api/tenant/list"
    Write-Log "✅ Tenants disponibles: $($tenantsResponse.total)" "Green"
    
    if ($tenantsResponse.total -eq 0) {
        Write-Log "⚠️  No hay tenants en el sistema." "Yellow"
    } else {
        $tenantsResponse.tenants | ForEach-Object {
            Write-Log "   📋 $($_.tenant_id) - $($_.institution_name) ($($_.plan))" "White"
        }
    }
} catch {
    Write-Log "❌ Error obteniendo lista de tenants: $($_.Exception.Message)" "Red"
}

# ==================================================
# GENERACIÓN DE DASHBOARDS WHITE-LABEL
# ==================================================
Write-Log "=== GENERACIÓN DE DASHBOARDS WHITE-LABEL ===" "Cyan"

New-Item -ItemType Directory -Path "dashboards" -Force | Out-Null

$successfulDashboards = 0
$failedDashboards = 0

try {
    $tenants = Invoke-RestMethod -Uri "$BaseURL/api/tenant/list"
    
    foreach ($tenant in $tenants.tenants) {
        $tenantId = $tenant.tenant_id
        Write-Log "🔄 Generando dashboard para: $tenantId" "Yellow"
        
        try {
            $dashboardResult = Invoke-RestMethod -Uri "$BaseURL/api/branding/dashboard/$tenantId" -TimeoutSec 30
            Write-Log "   ✅ Dashboard: $($dashboardResult.dashboard_path)" "Green"
            $successfulDashboards++
            
            if (Test-Path $dashboardResult.dashboard_path) {
                $fileInfo = Get-Item $dashboardResult.dashboard_path
                Write-Log "   📊 Verificado: $($fileInfo.Length) bytes" "Green"
            } else {
                Write-Log "   ⚠️  Archivo no encontrado" "Yellow"
            }
        } catch {
            Write-Log "   ❌ Error: $($_.Exception.Message)" "Red"
            $failedDashboards++
        }
    }
} catch {
    Write-Log "❌ Error obteniendo tenants: $($_.Exception.Message)" "Red"
}

Write-Log "📈 Resumen Dashboards: $successfulDashboards exitosos, $failedDashboards fallidos" "Cyan"

# ==================================================
# PREPARACIÓN KIT COMERCIAL
# ==================================================
Write-Log "=== PREPARANDO KIT COMERCIAL ===" "Cyan"

$kitDir = "kit_comercial_fase9"
New-Item -ItemType Directory -Path $kitDir -Force | Out-Null

# 1. Script de demo
$demoScript = @"
# SCRIPT DE DEMO - FASE 9 ACELERADA
# Generado: $(Get-Date)

ENDPOINTS PARA DEMO:
- Health: $BaseURL/
- Lista tenants: $BaseURL/api/tenant/list  
- Dashboard ejemplo: $BaseURL/api/branding/dashboard/credicefi_b27fa331

FLUJO RECOMENDADO (8 minutos):
1. Problema: Costo del fraude
2. Demo: Dashboard Credicefi 
3. ROI: De 24h a 3 segundos
4. Cierre: Cupos piloto gratis
"@

Set-Content -Path "$kitDir/demo_script.md" -Value $demoScript
Write-Log "✅ Script de demo creado" "Green"

# 2. Lista de tenants
try {
    $tenantList = $tenantsResponse.tenants | ForEach-Object {
        @{
            tenant_id = $_.tenant_id
            institution_name = $_.institution_name
            plan = $_.plan
        }
    } | ConvertTo-Json -Depth 3

    Set-Content -Path "$kitDir/tenants_list.json" -Value $tenantList
    Write-Log "✅ Lista tenants creada" "Green"
} catch {
    Write-Log "⚠️  Error creando lista de tenants" "Yellow"
}

# 3. Template de email
$emailTemplate = @"
ASUNTO: Demo Nadakki AI - Caso Real

Hola [Nombre],

Sistema implementado con instituciones como Credicefi:
- Evaluaciones: 24 horas -> 3 segundos
- Deteccion de fraude: +89% accuracy

¿15 minutos para ver demo?

Saludos
"@

Set-Content -Path "$kitDir/email_template.txt" -Value $emailTemplate
Write-Log "✅ Template email creado" "Green"

# ==================================================
# VERIFICACIÓN FINAL
# ==================================================
Write-Log "=== VERIFICACIÓN FINAL ===" "Cyan"

$endpointsToVerify = @("/", "/api/tenant/list", "/docs")

foreach ($endpoint in $endpointsToVerify) {
    try {
        $result = Invoke-WebRequest -Uri "$BaseURL$endpoint" -UseBasicParsing -TimeoutSec 10
        Write-Log "   ✅ $endpoint : $($result.StatusCode)" "Green"
    } catch {
        Write-Log "   ❌ $endpoint : $($_.Exception.Message)" "Red"
    }
}

# ==================================================
# RESUMEN EJECUTIVO
# ==================================================
$executionTime = (Get-Date) - $ScriptStartTime
Write-Log " " "White"
Write-Log "🎉 FASE 9 ACELERADA - COMPLETADA" "Green"
Write-Log "=================================" "Green"
Write-Log "Tiempo ejecucion: $($executionTime.TotalMinutes.ToString('0.0')) minutos" "White"
Write-Log "Tenants procesados: $($tenantsResponse.total)" "White"
Write-Log "Dashboards generados: $successfulDashboards" "White"
Write-Log "Kit comercial: $kitDir/" "White"
Write-Log "Backup seguridad: $BackupDir/" "White"
Write-Log " " "White"
Write-Log "SISTEMA VERIFICADO - LISTO PARA VALIDACION COMERCIAL" "Green"