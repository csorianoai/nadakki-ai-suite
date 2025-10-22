# EMERGENCY BACKUP - SIN GIT
# Ejecutar desde: C:\Users\cesar\Projects\nadakki-ai-suite\nadakki-ai-suite

Write-Host "🚨 BACKUP DE EMERGENCIA - FLUJO B DORADO" -ForegroundColor Red

# 1. Verificar ubicación
$currentPath = Get-Location
Write-Host "Directorio actual: $currentPath" -ForegroundColor Yellow

if ($currentPath -notlike "*nadakki-ai-suite\nadakki-ai-suite") {
    Write-Host "❌ ERROR: No estás en el directorio correcto" -ForegroundColor Red
    Write-Host "Ejecuta: cd C:\Users\cesar\Projects\nadakki-ai-suite\nadakki-ai-suite" -ForegroundColor Yellow
    exit 1
}

# 2. Crear backup con timestamp
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "backup_golden_$timestamp"
mkdir $backupDir

Write-Host "✅ Creando backup en: $backupDir" -ForegroundColor Green

# 3. Listar archivos del proyecto REAL
Write-Host "`n=== ARCHIVOS EN EL PROYECTO ===" -ForegroundColor Cyan
$projectFiles = Get-ChildItem -File -Name | Sort-Object
$projectFiles | ForEach-Object { Write-Host "  $_" }

Write-Host "`n=== CARPETAS EN EL PROYECTO ===" -ForegroundColor Cyan  
$projectFolders = Get-ChildItem -Directory -Name | Sort-Object
$projectFolders | ForEach-Object { Write-Host "  $_" }

# 4. Backup de archivos críticos del proyecto
$criticalFiles = @(
    "*.py",
    "*.php", 
    "*.txt",
    "*.md",
    "*.js",
    "*.css",
    "*.json"
)

Write-Host "`n=== HACIENDO BACKUP ===" -ForegroundColor Green

foreach ($pattern in $criticalFiles) {
    $files = Get-ChildItem -File -Name $pattern -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        Copy-Item $file "$backupDir\"
        Write-Host "✅ Backup: $file" -ForegroundColor Green
    }
}

# 5. Backup de carpetas importantes
$importantFolders = @("templates", "includes", "assets", "core", "agents", "config", "models", "services", "utils")

foreach ($folder in $importantFolders) {
    if (Test-Path $folder -PathType Container) {
        Copy-Item $folder "$backupDir\" -Recurse -Force
        Write-Host "✅ Backup folder: $folder" -ForegroundColor Green
    }
}

# 6. Crear manifiesto del backup
$manifest = @{
    timestamp = $timestamp
    location = $currentPath.ToString()
    files_backed_up = (Get-ChildItem "$backupDir" -Recurse -File).Count
    total_size_mb = [math]::Round((Get-ChildItem "$backupDir" -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB, 2)
}

$manifest | ConvertTo-Json | Out-File "$backupDir\manifest.json"

Write-Host "`n🎯 BACKUP COMPLETADO EXITOSAMENTE" -ForegroundColor Green
Write-Host "Ubicación: $backupDir" -ForegroundColor Green
Write-Host "Archivos: $($manifest.files_backed_up)" -ForegroundColor Green
Write-Host "Tamaño: $($manifest.total_size_mb) MB" -ForegroundColor Green

# 7. Verificar que el backend sigue funcionando
Write-Host "`n=== VERIFICANDO BACKEND ===" -ForegroundColor Cyan

try {
    $healthResponse = Invoke-RestMethod -Uri "https://6jbuszwhjd.execute-api.us-east-2.amazonaws.com/prod/api/v1/health" -Method GET -TimeoutSec 10
    Write-Host "✅ Backend: ONLINE" -ForegroundColor Green
    Write-Host "Status: $($healthResponse.status)" -ForegroundColor Green
}
catch {
    Write-Host "❌ Backend: ERROR - $($_.Exception.Message)" -ForegroundColor Red
}

# 8. Test de evaluación para confirmar Flujo B
Write-Host "`n=== VALIDANDO FLUJO B ===" -ForegroundColor Cyan

try {
    $profile = @{
        client_id = "GOLDEN_BACKUP_TEST"
        income = 50000
        credit_score = 750
        age = 32
        debt_to_income = 0.3
    }
    
    $json = $profile | ConvertTo-Json
    $startTime = Get-Date
    
    $evalResponse = Invoke-RestMethod -Uri "https://6jbuszwhjd.execute-api.us-east-2.amazonaws.com/prod/api/v1/evaluate" `
        -Method POST `
        -Body $json `
        -ContentType "application/json" `
        -Headers @{"X-Tenant-ID" = "bank01"} `
        -TimeoutSec 15
    
    $endTime = Get-Date
    $responseTime = ($endTime - $startTime).TotalMilliseconds
    
    Write-Host "✅ FLUJO B: EXITOSO" -ForegroundColor Green
    Write-Host "Response Time: $([math]::Round($responseTime, 2))ms" -ForegroundColor Green
    Write-Host "Score: $($evalResponse.data.quantum_similarity_score)" -ForegroundColor Green
    Write-Host "Risk Level: $($evalResponse.data.risk_level)" -ForegroundColor Green
    Write-Host "Source: $($evalResponse.source)" -ForegroundColor Green
    
    # Guardar respuesta dorada
    $evalResponse | ConvertTo-Json -Depth 5 | Out-File "$backupDir\flujo_b_golden_response.json"
    
    Write-Host "`n🏆 FLUJO B CONFIRMADO COMO DORADO" -ForegroundColor Green
    
}
catch {
    Write-Host "❌ FLUJO B: ERROR - $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n📂 ARCHIVOS DE BACKUP CREADOS:" -ForegroundColor Yellow
Get-ChildItem $backupDir | ForEach-Object { Write-Host "  $($_.Name)" }

Write-Host "`n✅ ESTADO DORADO PRESERVADO SIN GIT" -ForegroundColor Green
Write-Host "Continuar con PROPUESTA 3A..." -ForegroundColor Yellow
