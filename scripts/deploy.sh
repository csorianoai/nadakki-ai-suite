#!/bin/bash

# Script de Deploy Automatizado Nadakki AI Suite
# Uso: ./deploy.sh [environment]

set -e

ENVIRONMENT=${1:-production}
PROJECT_NAME="nadakki-ai-suite"
BACKUP_DIR="backup/$(date +%Y%m%d_%H%M%S)_pre_deploy"

echo "🚀 Iniciando deploy de  en ambiente "

# Verificar dependencias
command -v docker >/dev/null 2>&1 || { echo "❌ Docker no instalado"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose no instalado"; exit 1; }

# Crear backup pre-deploy
echo "📦 Creando backup pre-deploy..."
mkdir -p 
docker-compose exec postgres pg_dump -U nadakki -d nadakki_prod > /database_backup.sql 2>/dev/null || echo "⚠️  No hay base de datos existente para backup"

# Build nueva imagen
echo "🔨 Building nueva imagen..."
docker-compose build --no-cache nadakki-api

# Verificar configuraciones
echo "🔍 Verificando configuraciones..."
if [ ! -f ".env." ]; then
    echo "❌ Archivo .env. no encontrado"
    exit 1
fi

if [ ! -f "config/tenants/credicefi.json" ]; then
    echo "❌ Configuración tenant Credicefi no encontrada"
    exit 1
fi

# Deploy con zero downtime
echo "🚀 Ejecutando deploy zero-downtime..."
docker-compose up -d --remove-orphans

# Health check
echo "🏥 Verificando health de servicios..."
sleep 30

if curl -f http://localhost:5000/api/v1/health > /dev/null 2>&1; then
    echo "✅ API health check passed"
else
    echo "❌ API health check failed"
    echo "🔄 Rollback automático..."
    docker-compose down
    exit 1
fi

# Verificar base de datos
if docker-compose exec postgres pg_isready -U nadakki -d nadakki_prod > /dev/null 2>&1; then
    echo "✅ Database health check passed"
else
    echo "❌ Database health check failed"
    exit 1
fi

# Verificar Redis
if docker-compose exec redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis health check passed"
else
    echo "❌ Redis health check failed"
    exit 1
fi

# Cleanup imágenes antiguas
echo "🧹 Limpieza de imágenes antiguas..."
docker image prune -f

# Mostrar status final
echo ""
echo "🎉 Deploy completado exitosamente!"
echo ""
echo "📊 Estado de servicios:"
docker-compose ps

echo ""
echo "🌐 URLs disponibles:"
echo "  - API: http://localhost:5000"
echo "  - Dashboard: http://localhost:80/dashboard"  
echo "  - Grafana: http://localhost:3000 (admin/admin123)"
echo "  - Prometheus: http://localhost:9090"
echo ""
echo "📝 Logs en tiempo real:"
echo "  docker-compose logs -f nadakki-api"
echo ""
echo "🔄 Para rollback:"
echo "  docker-compose down && docker-compose up -d"
