#!/usr/bin/env pwsh
# 🧪 NADAKKI TESTING SUITE - SIMPLE & FAST

$ErrorActionPreference = "Stop"
$passed = 0
$failed = 0
$total = 0

$ProjectRoot = "C:\Users\cesar\Projects\nadakki-ai-suite\nadakki-ai-suite"
Set-Location $ProjectRoot

Write-Host "`n" -NoNewline
Write-Host "╔════════════════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  🧪 NADAKKI v6.0 - AUTOMATED TESTING SUITE" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Green

function Test {
    param([string]$Name, [scriptblock]$Check)
    $total++
    Write-Host "   🔍 $Name..." -NoNewline -ForegroundColor Cyan
    try {
        & $Check
        Write-Host " ✅" -ForegroundColor Green
        $passed++
    }
    catch {
        Write-Host " ❌" -ForegroundColor Red
        Write-Host "      Error: $($_.Exception.Message)" -ForegroundColor DarkRed
        $failed++
    }
}

Write-Host "`n📁 FASE 1: ARCHIVOS (11/11)" -ForegroundColor Green

Test "tenant_manager.py" { if (-not (Test-Path "core/multi_tenancy/tenant_manager.py")) { throw "Not found" } }
Test "main.py (API)" { if (-not (Test-Path "api/v1/tenants/main.py")) { throw "Not found" } }
Test "SQL schema" { if (-not (Test-Path "database/migrations/001_multi_tenant_enterprise_schema.sql")) { throw "Not found" } }
Test "banreservas config" { if (-not (Test-Path "institutions/banreservas/config.json")) { throw "Not found" } }
Test "credicefi config" { if (-not (Test-Path "institutions/credicefi/config.json")) { throw "Not found" } }
Test "template config" { if (-not (Test-Path "institutions/templates/institution.template.json")) { throw "Not found" } }
Test "docker-compose.yml" { if (-not (Test-Path "docker-compose.yml")) { throw "Not found" } }
Test "Dockerfile" { if (-not (Test-Path "Dockerfile")) { throw "Not found" } }
Test "requirements.txt" { if (-not (Test-Path "requirements.txt")) { throw "Not found" } }
Test ".env.example" { if (-not (Test-Path ".env.example")) { throw "Not found" } }
Test "README_v6.md" { if (-not (Test-Path "README_v6.md")) { throw "Not found" } }

Write-Host "`n🐍 FASE 2: PYTHON SYNTAX" -ForegroundColor Green

Test "Python installed" {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) { throw "Python not found" }
}

Test "tenant_manager.py syntax" {
    python -m py_compile "core/multi_tenancy/tenant_manager.py" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Syntax error" }
}

Test "main.py syntax" {
    python -m py_compile "api/v1/tenants/main.py" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Syntax error" }
}

Write-Host "`n📋 FASE 3: JSON VALIDATION" -ForegroundColor Green

Test "banreservas JSON" {
    $json = Get-Content "institutions/banreservas/config.json" -Raw | ConvertFrom-Json
    if ($json.institution.id -ne "org_banreservas") { throw "ID mismatch" }
}

Test "credicefi JSON" {
    $json = Get-Content "institutions/credicefi/config.json" -Raw | ConvertFrom-Json
    if ($json.institution.id -ne "org_credicefi") { throw "ID mismatch" }
}

Test "template JSON" {
    $json = Get-Content "institutions/templates/institution.template.json" -Raw | ConvertFrom-Json
    if (-not $json) { throw "Invalid JSON" }
}

Test "Both have api_keys" {
    $j1 = (Get-Content "institutions/banreservas/config.json" -Raw) | ConvertFrom-Json
    $j2 = (Get-Content "institutions/credicefi/config.json" -Raw) | ConvertFrom-Json
    if (-not $j1.api_keys.api_key -or -not $j2.api_keys.api_key) { throw "Missing api_key" }
}

Write-Host "`n🐳 FASE 4: DOCKER VALIDATION" -ForegroundColor Green

Test "Docker installed" {
    $docker = Get-Command docker -ErrorAction SilentlyContinue
    if (-not $docker) { throw "Docker not found" }
}

Test "Docker running" {
    docker ps 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Docker not running" }
}

Test "docker-compose installed" {
    $dc = Get-Command docker-compose -ErrorAction SilentlyContinue
    if (-not $dc) { throw "docker-compose not found" }
}

Test "docker-compose.yml has postgres" {
    $content = Get-Content "docker-compose.yml" -Raw
    if ($content -notmatch "postgres") { throw "PostgreSQL not found" }
}

Test "docker-compose.yml has redis" {
    $content = Get-Content "docker-compose.yml" -Raw
    if ($content -notmatch "redis") { throw "Redis not found" }
}

Test "docker-compose.yml has api" {
    $content = Get-Content "docker-compose.yml" -Raw
    if ($content -notmatch "api") { throw "API service not found" }
}

Write-Host "`n📦 FASE 5: DEPENDENCIES" -ForegroundColor Green

Test "requirements.txt not empty" {
    $lines = @(Get-Content "requirements.txt" | Where-Object { $_ -ne "" })
    if ($lines.Count -lt 10) { throw "Too small" }
}

Test "FastAPI in requirements" {
    if ((Get-Content "requirements.txt" -Raw) -notmatch "fastapi") { throw "Not found" }
}

Test "SQLAlchemy in requirements" {
    if ((Get-Content "requirements.txt" -Raw) -notmatch "sqlalchemy") { throw "Not found" }
}

Test "Redis in requirements" {
    if ((Get-Content "requirements.txt" -Raw) -notmatch "redis") { throw "Not found" }
}

Test "Uvicorn in requirements" {
    if ((Get-Content "requirements.txt" -Raw) -notmatch "uvicorn") { throw "Not found" }
}

Write-Host "`n⚙️  FASE 6: ENVIRONMENT CONFIG" -ForegroundColor Green

Test ".env.example exists" {
    if (-not (Test-Path ".env.example")) { throw "Not found" }
}

Test "DATABASE_URL in .env" {
    if ((Get-Content ".env.example" -Raw) -notmatch "DATABASE_URL") { throw "Not found" }
}

Test "REDIS_URL in .env" {
    if ((Get-Content ".env.example" -Raw) -notmatch "REDIS_URL") { throw "Not found" }
}

Test "API_PORT in .env" {
    if ((Get-Content ".env.example" -Raw) -notmatch "API_PORT") { throw "Not found" }
}

Write-Host "`n📊 FASE 7: DATABASE SCHEMA" -ForegroundColor Green

Test "SQL has CREATE TABLE" {
    $sql = Get-Content "database/migrations/001_multi_tenant_enterprise_schema.sql" -Raw
    if ($sql -notmatch "CREATE TABLE") { throw "Not found" }
}

Test "SQL has institutions table" {
    $sql = Get-Content "database/migrations/001_multi_tenant_enterprise_schema.sql" -Raw
    if ($sql -notmatch "institutions") { throw "Not found" }
}

Test "SQL has RLS enabled" {
    $sql = Get-Content "database/migrations/001_multi_tenant_enterprise_schema.sql" -Raw
    if ($sql -notmatch "ENABLE ROW LEVEL SECURITY") { throw "Not found" }
}

Test "SQL has audit_logs" {
    $sql = Get-Content "database/migrations/001_multi_tenant_enterprise_schema.sql" -Raw
    if ($sql -notmatch "audit_logs") { throw "Not found" }
}

Write-Host "`n📚 FASE 8: DOCUMENTATION" -ForegroundColor Green

Test "README exists" {
    if (-not (Test-Path "README_v6.md")) { throw "Not found" }
}

Test "README has content" {
    $content = Get-Content "README_v6.md" -Raw
    if ($content.Length -lt 100) { throw "Too small" }
}

Test "README has Quick Start" {
    $content = Get-Content "README_v6.md" -Raw
    if ($content -notmatch "Quick Start|Installation") { throw "Not found" }
}

Write-Host "`n📁 FASE 9: FOLDERS" -ForegroundColor Green

Test "core/multi_tenancy folder" { if (-not (Test-Path "core/multi_tenancy")) { throw "Not found" } }
Test "api/v1/tenants folder" { if (-not (Test-Path "api/v1/tenants")) { throw "Not found" } }
Test "database/migrations folder" { if (-not (Test-Path "database/migrations")) { throw "Not found" } }
Test "institutions folder" { if (-not (Test-Path "institutions")) { throw "Not found" } }
Test "tests folder" { if (-not (Test-Path "tests")) { throw "Not found" } }
Test "docs folder" { if (-not (Test-Path "docs")) { throw "Not found" } }

Write-Host "`n🔍 FASE 10: CODE INTEGRITY" -ForegroundColor Green

Test "TenantManager class" {
    $content = Get-Content "core/multi_tenancy/tenant_manager.py" -Raw
    if ($content -notmatch "class TenantManager") { throw "Not found" }
}

Test "TenantManager __init__" {
    $content = Get-Content "core/multi_tenancy/tenant_manager.py" -Raw
    if ($content -notmatch "def __init__") { throw "Not found" }
}

Test "FastAPI app" {
    $content = Get-Content "api/v1/tenants/main.py" -Raw
    if ($content -notmatch "app = FastAPI") { throw "Not found" }
}

Test "API /health endpoint" {
    $content = Get-Content "api/v1/tenants/main.py" -Raw
    if ($content -notmatch '@app.get.*health') { throw "Not found" }
}

Test "API /api/v1/tenants endpoint" {
    $content = Get-Content "api/v1/tenants/main.py" -Raw
    if ($content -notmatch '@app.get.*tenants') { throw "Not found" }
}

Write-Host "`n" -NoNewline
Write-Host "╔════════════════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  📊 RESULTADOS FINALES" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Green

$percentage = if ($total -gt 0) { [Math]::Round(($passed / $total) * 100, 0) } else { 0 }

Write-Host "`n   Total Tests: $total" -ForegroundColor White
Write-Host "   ✅ Passed:   $passed ($percentage%)" -ForegroundColor Green
Write-Host "   ❌ Failed:   $failed" -ForegroundColor Red

if ($failed -eq 0 -and $total -gt 0) {
    Write-Host "`n   ✨ ¡TODAS LAS PRUEBAS PASARON! ✨" -ForegroundColor Green
    Write-Host "`n   📋 PRÓXIMOS PASOS:" -ForegroundColor Yellow
    Write-Host "   1. cp .env.example .env" -ForegroundColor Cyan
    Write-Host "   2. docker-compose up -d" -ForegroundColor Cyan
    Write-Host "   3. pip install -r requirements.txt" -ForegroundColor Cyan
    Write-Host "   4. python -m uvicorn api.v1.tenants.main:app --reload" -ForegroundColor Cyan
}
else {
    Write-Host "`n   ⚠️  Revisa los errores arriba" -ForegroundColor Red
}

Write-Host "`n"
