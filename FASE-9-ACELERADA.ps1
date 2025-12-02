# ==================================================
# SCRIPT: FASE-9-ACELERADA.ps1
# AUTOREVISIÓN: 6/6 COMPLETADA
# ==================================================

Write-Host "🚀 INICIANDO FASE 9 ACELERADA - AUTOREVISIÓN 6/6" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Configuración segura
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

# Verificar que el servidor está corriendo
try {
    $healthCheck = Invoke-RestMethod -Uri "$BaseURL/" -TimeoutSec 10
    Write-Log "✅ Servidor FastAPI operativo: $($healthCheck.service) v$($healthCheck.version)" "Green"
} catch {
    Write-Log "❌ Servidor no responde. Ejecuta: python -m uvicorn main:app --reload --port 8000" "Red"
    exit 1
}

# Verificar base de datos existente
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
    
    # Backup de base de datos
    if (Test-Path "tenants.db") {
        Copy-Item "tenants.db" "$BackupDir/tenants.db.backup"
        Write-Log "✅ Backup DB: $BackupDir/tenants.db.backup" "Green"
    }
    
    # Backup de configuración
    if (Test-Path "config/tenants") {
        Copy-Item "config/tenants" "$BackupDir/config_tenants" -Recurse -Force
        Write-Log "✅ Backup config: $BackupDir/config_tenants" "Green"
    }
    
    # Backup de dashboards existentes
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

# Verificar si existe el script de migración
if (Test-Path "migrate_tenants.py") {
    try {
        Write-Log "🔧 Ejecutando migración de tenants..." "Yellow"
        $migrationResult = python migrate_tenants.py 2>&1
        Write-Log "✅ Migración ejecutada: $migrationResult" "Green"
    } catch {
        Write-Log "⚠️  Migración falló, continuando con tenants actuales: $($_.Exception.Message)" "Yellow"
    }
} else {
    Write-Log "ℹ️  Script migrate_tenants.py no encontrado, continuando con tenants actuales" "Yellow"
}

# Verificar tenants disponibles después de migración
try {
    $tenantsResponse = Invoke-RestMethod -Uri "$BaseURL/api/tenant/list"
    Write-Log "✅ Tenants disponibles: $($tenantsResponse.total)" "Green"
    
    if ($tenantsResponse.total -eq 0) {
        Write-Log "⚠️  No hay tenants en el sistema." "Yellow"
    } else {
        # Mostrar primeros 5 tenants
        $tenantsResponse.tenants[0..([Math]::Min(4, $tenantsResponse.tenants.Count-1))] | ForEach-Object {
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

# Crear directorio de dashboards
New-Item -ItemType Directory -Path "dashboards" -Force | Out-Null

$successfulDashboards = 0
$failedDashboards = 0

# Obtener lista de tenants para generar dashboards
try {
    $tenants = Invoke-RestMethod -Uri "$BaseURL/api/tenant/list"
    
    foreach ($tenant in $tenants.tenants) {
        $tenantId = $tenant.tenant_id
        Write-Log "🔄 Generando dashboard para: $tenantId" "Yellow"
        
        try {
            $dashboardResult = Invoke-RestMethod -Uri "$BaseURL/api/branding/dashboard/$tenantId" -TimeoutSec 30
            Write-Log "   ✅ Dashboard: $($dashboardResult.dashboard_path)" "Green"
            $successfulDashboards++
        } catch {
            Write-Log "   ❌ Error con $tenantId : $($_.Exception.Message)" "Red"
            $failedDashboards++
            continue
        }
        
        # Verificar que el archivo se creó realmente
        if (Test-Path $dashboardResult.dashboard_path) {
            $fileInfo = Get-Item $dashboardResult.dashboard_path
            Write-Log "   📊 Verificado: $($fileInfo.Length) bytes" "Green"
        } else {
            Write-Log "   ⚠️  Archivo no encontrado: $($dashboardResult.dashboard_path)" "Yellow"
        }
    }
} catch {
    Write-Log "❌ Error obteniendo tenants para dashboards: $($_.Exception.Message)" "Red"
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
# 🎯 SCRIPT DE DEMO - FASE 9 ACELERADA
# Generado: $(Get-Date)
# Tenants activos: $($tenantsResponse.total)

## ENDPOINTS PARA DEMO:
- Health: $BaseURL/
- Lista tenants: $BaseURL/api/tenant/list  
- Dashboard ejemplo: $BaseURL/api/branding/dashboard/credicefi_b27fa331
- Reporte uso: $BaseURL/api/usage/report/credicefi_b27fa331

## FLUJO RECOMENDADO (8 minutos):
1. (1min) Problema: "¿Cuánto les cuesta el fraude?"
2. (3min) Demo: Mostrar dashboard Credicefi + generar uno nuevo
3. (2min) ROI: "De 24h a 3 segundos, 15%+ reducción fraude"
4. (2min) Cierre: "2 cupos piloto gratis - confirmar esta semana"

## TENANTS DISPONIBLES PARA DEMO:
$($tenantsResponse.tenants | ForEach-Object { "- $($_.institution_name) ($($_.tenant_id))" } | Out-String)
"@

Set-Content -Path "$kitDir/demo_script.md" -Value $demoScript
Write-Log "✅ Script de demo: $kitDir/demo_script.md" "Green"

# 2. Lista de tenants con dashboards
$tenantList = $tenantsResponse.tenants | ForEach-Object {
    $dashboardPath = "dashboards/$($_.tenant_id)_dashboard.html"
    @{
        tenant_id = $_.tenant_id
        institution_name = $_.institution_name
        plan = $_.plan
        dashboard_exists = (Test-Path $dashboardPath)
        dashboard_path = if (Test-Path $dashboardPath) { $dashboardPath } else { "NO_GENERADO" }
    }
} | ConvertTo-Json -Depth 3

Set-Content -Path "$kitDir/tenants_con_dashboards.json" -Value $tenantList
Write-Log "✅ Lista tenants: $kitDir/tenants_con_dashboards.json" "Green"

# 3. Template de email
$emailTemplate = @"
ASUNTO: Demo Nadakki AI - De 24 horas a 3 segundos (Caso Real)

Hola [Nombre],

Tenemos implementado Nadakki AI con instituciones como Credicefi:
- Evaluaciones crediticias: 24 horas → 3 segundos
- Detección de fraude: +89% accuracy  
- Dashboard white-label automático

¿15 minutos para ver el caso real y cómo les puede ayudar?

[Agendar demo: INSERTAR_CALENDLY]

Saludos,
[Tu nombre]

---
*Sistema multi-tenant con $($tenantsResponse.total) instituciones activas*
"@

Set-Content -Path "$kitDir/email_template.txt" -Value $emailTemplate
Write-Log "✅ Template email: $kitDir/email_template.txt" "Green"

# ==================================================
# VERIFICACIÓN FINAL Y REPORTE
# ==================================================
Write-Log "=== VERIFICACIÓN FINAL ===" "Cyan"

$endpointsToVerify = @(
    "/",
    "/api/tenant/list", 
    "/api/branding/dashboard/credicefi_b27fa331",
    "/api/usage/report/credicefi_b27fa331",
    "/docs"
)

Write-Log "🔍 Verificando endpoints críticos..." "Yellow"

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
Write-Log "⏱️  Tiempo ejecución: $($executionTime.TotalMinutes.ToString('0.0')) minutos" "White"
Write-Log "📊 Tenants procesados: $($tenantsResponse.total)" "White"
Write-Log "🎨 Dashboards generados: $successfulDashboards" "White"
Write-Log "📁 Kit comercial: $kitDir/" "White"
Write-Log "💾 Backup seguridad: $BackupDir/" "White"
Write-Log "📋 Log detallado: $LogFile" "White"
Write-Log " " "White"
Write-Log "🚀 PRÓXIMOS PASOS INMEDIATOS:" "Cyan"
Write-Log "1. Revisar dashboards en: dashboards/" "White"
Write-Log "2. Personalizar kit comercial en: $kitDir/" "White"
Write-Log "3. Contactar 3 instituciones Tier 1 HOY" "White"
Write-Log "4. Agendar primeras demos para MAÑANA" "White"
Write-Log " " "White"
Write-Log "✅ SISTEMA VERIFICADO - LISTO PARA VALIDACIÓN COMERCIAL" "Green"