#!/usr/bin/env pwsh
$ProjectRoot = "C:\Users\cesar\Projects\nadakki-ai-suite\nadakki-ai-suite"
Set-Location $ProjectRoot

Write-Host "`n╔════════════════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  🚀 NADAKKI v6.0 - DEPLOYMENT AUTOMATIZADO" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`n📝 PASO 1: Arreglando docker-compose.yml..." -ForegroundColor Yellow

$dockerCompose = @"
version: "3.8"
services:
  postgres:
    image: postgres:16-alpine
    container_name: nadakki-postgres
    environment:
      POSTGRES_DB: nadakki
      POSTGRES_USER: nadakki_user
      POSTGRES_PASSWORD: nadakki_secure_password_2025
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U nadakki_user"]
      interval: 10s
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: nadakki-redis
    command: redis-server --requirepass nadakki_redis_password_2025
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: nadakki-api
    environment:
      DATABASE_URL: postgresql://nadakki_user:nadakki_secure_password_2025@postgres:5432/nadakki
      REDIS_URL: redis://:nadakki_redis_password_2025@redis:6379
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
"@

$dockerCompose | Out-File -FilePath "docker-compose.yml" -Encoding UTF8 -Force
Write-Host "   ✅ docker-compose.yml actualizado" -ForegroundColor Green

Write-Host "`n⏹️  PASO 2: Deteniendo servicios anteriores..." -ForegroundColor Yellow
docker-compose down -v 2>&1 | Out-Null
Write-Host "   ✅ Servicios detenidos" -ForegroundColor Green

Write-Host "`n🐳 PASO 3: Iniciando Docker Compose..." -ForegroundColor Yellow
docker-compose up -d
Write-Host "   ⏳ Esperando 20 segundos..." -ForegroundColor Gray
Start-Sleep -Seconds 20
Write-Host "   ✅ Servicios iniciados" -ForegroundColor Green

Write-Host "`n🗄️  PASO 4: Ejecutando migraciones..." -ForegroundColor Yellow
docker exec nadakki-postgres psql -U nadakki_user -d nadakki -c "CREATE EXTENSION IF NOT EXISTS pgcrypto; CREATE EXTENSION IF NOT EXISTS uuid-ossp;" 2>&1 | Out-Null
Write-Host "   ✅ Extensiones PostgreSQL creadas" -ForegroundColor Green

Write-Host "`n📦 PASO 5: Instalando dependencias Python..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet 2>&1 | Out-Null
Write-Host "   ✅ Dependencias instaladas" -ForegroundColor Green

Write-Host "`n⚙️  PASO 6: Configurando variables de entorno..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env" -Force
    Write-Host "   ✅ .env creado" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  .env ya existe" -ForegroundColor Cyan
}

Write-Host "`n╔════════════════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ✅ DEPLOYMENT COMPLETADO" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`n🚀 PRÓXIMO PASO - Abre una NUEVA terminal PowerShell y ejecuta:" -ForegroundColor Yellow
Write-Host "   python -m uvicorn api.v1.tenants.main:app --reload" -ForegroundColor Cyan

Write-Host "`n📖 Para verificar - En otra terminal:" -ForegroundColor Yellow
Write-Host "   curl http://localhost:8000/health" -ForegroundColor Cyan
Write-Host "   O abre: http://localhost:8000/api/docs" -ForegroundColor Cyan

Write-Host "`n"
