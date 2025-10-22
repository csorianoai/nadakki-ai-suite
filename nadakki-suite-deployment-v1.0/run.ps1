# run.ps1
Write-Host "`n🚀 Ejecutando Nadakki AI Suite Runtime..." -ForegroundColor Cyan

# Ruta base
$projectRoot = "C:\Users\cesar\Projects\nadakki-ai-suite\nadakki-ai-suite\nadakki-suite-deployment-v1.0"

# Activar entorno virtual
$venvActivate = "C:\Users\cesar\Projects\nadakki-ai-suite\nadakki-ai-suite\nadakki_env_clean\Scripts\Activate.ps1"

if (-Not (Test-Path $venvActivate)) {
    Write-Host "❌ Entorno virtual no encontrado en: $venvActivate" -ForegroundColor Red
    exit
}

Write-Host "✅ Activando entorno virtual..." -ForegroundColor Green
& $venvActivate

# Ir al runtime
$runtimePath = Join-Path $projectRoot "runtime"
Set-Location $runtimePath

# Verificar que main.py existe
if (-Not (Test-Path "main.py")) {
    Write-Host "❌ Archivo main.py no encontrado en: $runtimePath" -ForegroundColor Red
    exit
}

# Ejecutar uvicorn
Write-Host "⚙️ Iniciando Uvicorn en http://127.0.0.1:8000 ..." -ForegroundColor Yellow
Start-Sleep -Seconds 1
uvicorn main:app --reload --port 8000
