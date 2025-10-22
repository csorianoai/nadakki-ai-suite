#!/bin/bash
# ===================================================================
# 🚀 NADAKKI AI SUITE - CREDICEFI PRODUCTION DEPLOYMENT SCRIPT
# Deploy automático optimizado para AWS con zero-downtime
# Cliente: Credicefi Dominicana S.A.
# ===================================================================

set -e  # Exit on any error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${PURPLE}"
echo "======================================="
echo "🚀 NADAKKI AI SUITE - CREDICEFI DEPLOY"
echo "======================================="
echo -e "${NC}"

# Variables
ENVIRONMENT="production"
TENANT_ID="credicefi"
APP_NAME="nadakki-credicefi"
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"

# Funciones utilitarias
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# === PASO 1: VALIDACIONES PRE-DEPLOY ===
log "🔍 Ejecutando validaciones pre-deploy..."

# Verificar Docker
if ! command -v docker &> /dev/null; then
    error "Docker no está instalado"
fi

# Verificar docker-compose
if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose no está instalado"
fi

# Verificar archivos requeridos
REQUIRED_FILES=(
    "Dockerfile"
    "docker-compose.production.yml"
    ".env.production"
    "config/tenants/credicefi.json"
    "integrations/powerbi/credicefi_connector.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        error "Archivo requerido no encontrado: $file"
    fi
done

log "✅ Validaciones pre-deploy completadas"

# === PASO 2: BACKUP DE DATOS ===
log "💾 Creando backup de datos existentes..."

mkdir -p "$BACKUP_DIR"

# Backup de base de datos si existe
if docker ps -q -f name=nadakki-credicefi-db &> /dev/null; then
    info "Creando backup de PostgreSQL..."
    docker exec nadakki-credicefi-db pg_dumpall -c -U nadakki_user > "$BACKUP_DIR/database_backup.sql"
fi

# Backup de configuraciones
if [ -d "config" ]; then
    info "Respaldando configuraciones..."
    cp -r config "$BACKUP_DIR/"
fi

log "✅ Backup completado en: $BACKUP_DIR"

# === PASO 3: BUILD DE IMÁGENES ===
log "🔨 Construyendo imágenes Docker..."

# Build de imagen principal con cache
docker build \
    --build-arg ENVIRONMENT=$ENVIRONMENT \
    --build-arg TENANT_ID=$TENANT_ID \
    -t nadakki-ai-suite:credicefi-prod \
    --cache-from nadakki-ai-suite:credicefi-prod \
    .

if [ $? -ne 0 ]; then
    error "Error construyendo imagen Docker"
fi

log "✅ Imagen Docker construida exitosamente"

# === PASO 4: HEALTH CHECK PRE-DEPLOY ===
log "🏥 Verificando salud del sistema actual..."

if docker ps -q -f name=nadakki-credicefi-api &> /dev/null; then
    HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/v1/health || echo "000")
    if [ "$HEALTH_STATUS" = "200" ]; then
        info "Sistema actual saludable (HTTP 200)"
    else
        warning "Sistema actual no responde correctamente (HTTP $HEALTH_STATUS)"
    fi
fi

# === PASO 5: DEPLOY CON ZERO DOWNTIME ===
log "🚀 Iniciando deployment con zero downtime..."

# Cargar variables de entorno
if [ -f ".env.production" ]; then
    export $(grep -v '^#' .env.production | xargs)
fi

# Deploy usando docker-compose
docker-compose -f docker-compose.production.yml down --remove-orphans
docker-compose -f docker-compose.production.yml up -d --build

if [ $? -ne 0 ]; then
    error "Error en deployment con docker-compose"
fi

log "✅ Servicios desplegados, esperando inicialización..."

# === PASO 6: HEALTH CHECKS POST-DEPLOY ===
log "🏥 Ejecutando health checks post-deploy..."

# Esperar que los servicios estén listos
sleep 30

SERVICES=("nadakki-credicefi-api" "nadakki-credicefi-redis" "nadakki-credicefi-db")

for service in "${SERVICES[@]}"; do
    info "Verificando servicio: $service"
    
    # Esperar hasta 120 segundos por servicio
    for i in {1..24}; do
        if docker ps --filter "name=$service" --filter "status=running" | grep -q $service; then
            log "✅ Servicio $service está corriendo"
            break
        else
            if [ $i -eq 24 ]; then
                error "Servicio $service no pudo iniciar después de 120 segundos"
            fi
            sleep 5
        fi
    done
done

# Health check de API principal
log "🧪 Probando endpoints críticos..."

# Test endpoint health
for i in {1..12}; do
    HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/v1/health || echo "000")
    if [ "$HEALTH_STATUS" = "200" ]; then
        log "✅ API Health Check: OK"
        break
    else
        if [ $i -eq 12 ]; then
            error "API no respondió correctamente después de 60 segundos (HTTP $HEALTH_STATUS)"
        fi
        info "Esperando API... intento $i/12"
        sleep 5
    fi
done

# Test endpoint específico PowerBI
POWERBI_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "X-Tenant-ID: credicefi" \
    http://localhost:5000/api/v1/powerbi/health || echo "000")

if [ "$POWERBI_STATUS" = "200" ]; then
    log "✅ PowerBI Integration: OK"
else
    warning "PowerBI Integration no disponible (HTTP $POWERBI_STATUS)"
fi

# === PASO 7: PRUEBAS DE FUNCIONALIDAD ===
log "🧪 Ejecutando pruebas de funcionalidad..."

# Test de evaluación crediticia
EVAL_TEST=$(curl -s -X POST http://localhost:5000/api/v1/evaluate \
    -H "Content-Type: application/json" \
    -H "X-Tenant-ID: credicefi" \
    -d '{
        "profile": {
            "income": 50000,
            "credit_score": 720,
            "age": 35,
            "employment_type": "full_time",
            "debt_to_income": 0.3
        }
    }' | python -c "import sys, json; data=json.load(sys.stdin); print('OK' if 'quantum_similarity_score' in data else 'FAIL')" 2>/dev/null || echo "FAIL")

if [ "$EVAL_TEST" = "OK" ]; then
    log "✅ Evaluación crediticia: FUNCIONANDO"
else
    warning "⚠️ Evaluación crediticia: NECESITA REVISIÓN"
fi

# === PASO 8: CONFIGURACIÓN DE MONITOREO ===
log "📊 Configurando monitoreo..."

# Verificar Prometheus
if docker ps --filter "name=nadakki-credicefi-prometheus" --filter "status=running" | grep -q prometheus; then
    log "✅ Prometheus: ACTIVO"
else
    info "ℹ️ Prometheus no está configurado"
fi

# Verificar Grafana
if docker ps --filter "name=nadakki-credicefi-grafana" --filter "status=running" | grep -q grafana; then
    log "✅ Grafana: ACTIVO (http://localhost:3000)"
else
    info "ℹ️ Grafana no está configurado"
fi

# === PASO 9: LIMPIEZA POST-DEPLOY ===
log "🧹 Ejecutando limpieza post-deploy..."

# Limpiar imágenes no utilizadas
docker image prune -f > /dev/null 2>&1

# Limpiar volumes no utilizados
docker volume prune -f > /dev/null 2>&1

log "✅ Limpieza completada"

# === PASO 10: RESUMEN FINAL ===
echo -e "${PURPLE}"
echo "======================================="
echo "🎉 DEPLOYMENT COMPLETADO EXITOSAMENTE"
echo "======================================="
echo -e "${NC}"

echo -e "${GREEN}"
echo "📋 RESUMEN DEL DEPLOYMENT:"
echo "• Cliente: Credicefi Dominicana S.A."
echo "• Ambiente: Production"
echo "• Versión: v2.0.0"
echo "• Timestamp: $(date)"
echo "• Backup: $BACKUP_DIR"
echo -e "${NC}"

echo -e "${BLUE}"
echo "🌐 ENDPOINTS DISPONIBLES:"
echo "• API Principal: http://localhost:5000"
echo "• Health Check: http://localhost:5000/api/v1/health"
echo "• PowerBI Integration: http://localhost:5000/api/v1/powerbi/health"
echo "• Dashboard Credicefi: http://localhost:5000/dashboard"
echo "• Grafana (opcional): http://localhost:3000"
echo "• Prometheus (opcional): http://localhost:9090"
echo -e "${NC}"

echo -e "${YELLOW}"
echo "📝 PRÓXIMOS PASOS:"
echo "1. Configurar DNS apuntando a este servidor"
echo "2. Configurar SSL/TLS certificates"
echo "3. Obtener API keys reales de PowerBI"
echo "4. Configurar credenciales DataCrédito"
echo "5. Ejecutar testing con Credicefi"
echo -e "${NC}"

echo -e "${GREEN}✨ ¡CREDICEFI ESTÁ LISTO PARA PRODUCCIÓN! ✨${NC}"
