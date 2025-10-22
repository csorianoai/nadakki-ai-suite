Write-Host "🚀 Iniciando instalación de Nadakki AI Suite..." -ForegroundColor Cyan

# Variables
$baseDir = Get-Location
$helmDir = Join-Path $baseDir "helm"
$runtimeDir = Join-Path $baseDir "runtime"
$sandboxDir = Join-Path $baseDir "sandbox_ui"
$configDir = Join-Path $baseDir "config"
$configFile = Join-Path $configDir "TENANT_TOKENS.json"

# Crear carpetas si no existen
foreach ($dir in @($helmDir, $runtimeDir, $sandboxDir, $configDir)) {
    if (-not (Test-Path $dir)) {
        Write-Host "📁 Creando carpeta: $dir" -ForegroundColor Yellow
        New-Item -ItemType Directory -Path $dir | Out-Null
    }
}

# Preparar archivos base
Write-Host "📦 Preparando plantillas de Helm y archivos de runtime..." -ForegroundColor Green

# Token de ejemplo
if (-not (Test-Path $configFile)) {
    Write-Host "🔐 Escribiendo archivo de tokens iniciales..." -ForegroundColor Green
    $tenantTokens = @{
        "credicefi" = "Bearer credicefi-token-123"
        "cofaci"    = "Bearer cofaci-token-456"
        "confisa"   = "Bearer confisa-token-789"
    }
    $tenantTokens | ConvertTo-Json -Depth 3 | Set-Content $configFile
}

# Final
Write-Host "`n✅ Nadakki AI Suite preparado correctamente en: $baseDir" -ForegroundColor Green
Write-Host "Puedes ahora ejecutar Helm, correr sandbox o iniciar el microservicio." -ForegroundColor Cyan
