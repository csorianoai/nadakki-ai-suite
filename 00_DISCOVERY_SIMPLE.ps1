# Discovery simplificado para Nadakki Collections
param([string]$Root = ".")

Write-Host "Iniciando discovery..." -ForegroundColor Green

$results = @{
    "timestamp" = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    "has_flask" = (Test-Path "app.py") -or (Test-Path "credicefi_api.py")
    "has_tenants" = (Test-Path "config\tenants\credicefi.json")
    "has_docker" = (Test-Path "docker-compose.yml")
    "has_monitoring" = (Test-Path "monitoring")
    "has_powerbi" = (Test-Path "powerbi_api.py")
}

# Mostrar resultados
Write-Host "Flask: $($results.has_flask)" -ForegroundColor Blue
Write-Host "Tenants: $($results.has_tenants)" -ForegroundColor Blue  
Write-Host "Docker: $($results.has_docker)" -ForegroundColor Blue
Write-Host "Monitoring: $($results.has_monitoring)" -ForegroundColor Blue
Write-Host "PowerBI: $($results.has_powerbi)" -ForegroundColor Blue

# Crear directorio docs
if (-not (Test-Path "docs")) { New-Item -ItemType Directory -Path "docs" -Force }

# Guardar STATE.json
$results | ConvertTo-Json | Set-Content "STATE.json" -Encoding UTF8
Write-Host "STATE.json creado" -ForegroundColor Green

Write-Host "DISCOVERY COMPLETADO" -ForegroundColor Green
Write-Host "Continuar con: .\00_write_files.ps1 -Root ." -ForegroundColor Yellow

Read-Host "Presiona Enter"
