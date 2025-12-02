# ============================================================================
# VALIDADOR DE FASES 81-85 - NADAKKI MULTI-TENANT
# ============================================================================

param(
    [string]$Action = "validate"
)

$ProjectRoot = Get-Location
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         VALIDADOR FASES 81-85: ARQUITECTURA MULTI-TENANT      ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "Proyecto: $ProjectRoot" -ForegroundColor Gray
Write-Host "Timestamp: $timestamp`n" -ForegroundColor Gray

# ============================================================================
# FASE 81: Database Setup
# ============================================================================
Write-Host "📊 FASE 81: DATABASE SETUP" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────────────" -ForegroundColor Gray

$checks = @{
    "✅ Schema SQL Generado" = "database/migrations/001_schema.sql"
    "✅ Archivo de Configuración" = ".env"
    "✅ Docker-Compose" = "docker-compose.yml"
    "✅ Documentación DB" = "database/README.md"
}

foreach ($check in $checks.GetEnumerator()) {
    $file = $check.Value
    if (Test-Path $file) {
        Write-Host "$($check.Key) → ✅ EXISTE" -ForegroundColor Green
    } else {
        Write-Host "$($check.Key) → ❌ FALTA" -ForegroundColor Red
    }
}

# Validar PostgreSQL
Write-Host "`n[Validando PostgreSQL...]" -ForegroundColor Gray
try {
    $dbCheck = docker exec nadakki-db psql -U postgres -d nadakki -c "\dt" 2>&1
    if ($dbCheck -like "*public*") {
        Write-Host "✅ PostgreSQL activo con tablas creadas" -ForegroundColor Green
    } else {
        Write-Host "⚠️  PostgreSQL activo pero sin tablas" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ PostgreSQL no está corriendo o no accessible" -ForegroundColor Red
}

# ============================================================================
# FASE 82: API REST Core
# ============================================================================
Write-Host "`n📡 FASE 82: API REST CORE" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────────────" -ForegroundColor Gray

$apiChecks = @{
    "✅ Main API" = "api/v1/tenants/main.py"
    "✅ Tenant Manager" = "core/multi_tenancy/tenant_manager.py"
    "✅ Requirements" = "requirements.txt"
    "✅ Documentación API" = "api/README.md"
}

foreach ($check in $apiChecks.GetEnumerator()) {
    $file = $check.Value
    if (Test-Path $file) {
        Write-Host "$($check.Key) → ✅ EXISTE" -ForegroundColor Green
    } else {
        Write-Host "$($check.Key) → ❌ FALTA" -ForegroundColor Red
    }
}

# Validar API ejecutándose
Write-Host "`n[Validando API FastAPI...]" -ForegroundColor Gray
try {
    $apiCheck = docker ps | Select-String "fastapi"
    if ($apiCheck) {
        Write-Host "✅ FastAPI container está corriendo" -ForegroundColor Green
        
        # Intentar llamada a API
        $response = curl -s -w "`n%{http_code}" http://localhost:8000/docs 2>&1
        if ($response -like "*200*") {
            Write-Host "✅ Swagger accesible en http://localhost:8000/docs" -ForegroundColor Green
        }
    } else {
        Write-Host "⚠️  FastAPI container no está corriendo" -ForegroundColor Yellow
        Write-Host "   Comando: docker-compose up -d" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Error validando API: $_" -ForegroundColor Red
}

# ============================================================================
# FASE 83: Webhook Processing
# ============================================================================
Write-Host "`n🔔 FASE 83: WEBHOOK PROCESSING" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────────────" -ForegroundColor Gray

$webhookChecks = @{
    "✅ Webhook Handlers" = "api/v1/webhooks/"
    "✅ Queue Processing" = "services/queue_processor.py"
    "✅ Redis Config" = "services/redis_config.py"
}

foreach ($check in $webhookChecks.GetEnumerator()) {
    $path = $check.Value
    if (Test-Path $path) {
        Write-Host "$($check.Key) → ✅ EXISTE" -ForegroundColor Green
    } else {
        Write-Host "$($check.Key) → ❌ FALTA" -ForegroundColor Red
    }
}

# Validar Redis
Write-Host "`n[Validando Redis...]" -ForegroundColor Gray
try {
    $redisCheck = docker ps | Select-String "redis"
    if ($redisCheck) {
        Write-Host "✅ Redis container está corriendo" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Redis container no está corriendo" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Error validando Redis" -ForegroundColor Red
}

# ============================================================================
# FASE 84: Payment Processing
# ============================================================================
Write-Host "`n💳 FASE 84: PAYMENT PROCESSING" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────────────" -ForegroundColor Gray

$paymentChecks = @{
    "✅ Stripe Integration" = "services/stripe_service.py"
    "✅ Payment Webhooks" = "api/v1/webhooks/stripe_webhook.py"
    "✅ Billing Service" = "services/billing_service.py"
}

foreach ($check in $paymentChecks.GetEnumerator()) {
    $file = $check.Value
    if (Test-Path $file) {
        Write-Host "$($check.Key) → ✅ EXISTE" -ForegroundColor Green
    } else {
        Write-Host "$($check.Key) → ❌ FALTA" -ForegroundColor Red
    }
}

# ============================================================================
# FASE 85: Notifications
# ============================================================================
Write-Host "`n📧 FASE 85: NOTIFICATIONS" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────────────" -ForegroundColor Gray

$notificationChecks = @{
    "✅ SendGrid Service" = "services/sendgrid_service.py"
    "✅ Email Templates" = "templates/emails/"
    "✅ Notification Queue" = "services/notification_queue.py"
}

foreach ($check in $notificationChecks.GetEnumerator()) {
    $path = $check.Value
    if (Test-Path $path) {
        Write-Host "$($check.Key) → ✅ EXISTE" -ForegroundColor Green
    } else {
        Write-Host "$($check.Key) → ❌ FALTA" -ForegroundColor Red
    }
}

# ============================================================================
# TESTS
# ============================================================================
Write-Host "`n🧪 TESTING" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────────────" -ForegroundColor Gray

$testChecks = @{
    "✅ Unit Tests" = "tests/unit/"
    "✅ Integration Tests" = "tests/integration/"
    "✅ Pytest Config" = "pytest.ini"
}

foreach ($check in $testChecks.GetEnumerator()) {
    $path = $check.Value
    if (Test-Path $path) {
        Write-Host "$($check.Key) → ✅ EXISTE" -ForegroundColor Green
    } else {
        Write-Host "$($check.Key) → ❌ FALTA" -ForegroundColor Red
    }
}

# Ejecutar tests si existen
if ((Test-Path "tests/") -and (Test-Path "pytest.ini")) {
    Write-Host "`n[Ejecutando tests...]" -ForegroundColor Gray
    try {
        $testResult = python -m pytest tests/ -v --tb=short 2>&1 | Tee-Object -Variable testOutput
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Todos los tests pasaron" -ForegroundColor Green
        } else {
            Write-Host "❌ Algunos tests fallaron (ver logs)" -ForegroundColor Red
        }
    } catch {
        Write-Host "⚠️  No se pudo ejecutar pytest" -ForegroundColor Yellow
    }
}

# ============================================================================
# RESUMEN FINAL
# ============================================================================
Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                       RESUMEN FINAL                            ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

Write-Host "`n✅ = Completado"
Write-Host "⚠️  = Parcial/No Corriendo"
Write-Host "❌ = Falta implementación"

Write-Host "`n📌 PRÓXIMOS PASOS:" -ForegroundColor Yellow
Write-Host "1. Ejecutar: docker-compose up -d"
Write-Host "2. Ejecutar tests: pytest tests/ -v"
Write-Host "3. Probar API: curl http://localhost:8000/docs"
Write-Host "4. Verificar BD: docker exec nadakki-db psql -U postgres -d nadakki -c 'SELECT * FROM tenants;'"