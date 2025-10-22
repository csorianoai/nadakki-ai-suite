Write-Host "=== BUSQUEDA EXHAUSTIVA DE AGENTES ===" -ForegroundColor Cyan

Write-Host "1. Buscando archivos Python con 'Agent' en el nombre..." -ForegroundColor Yellow
Get-ChildItem -Recurse -Filter "*Agent*.py" | ForEach-Object { Write-Host "  $($_.FullName)" -ForegroundColor Green }

Write-Host "
2. Buscando archivos Python con 'agent' minusculas..." -ForegroundColor Yellow  
Get-ChildItem -Recurse -Filter "*agent*.py" | ForEach-Object { Write-Host "  $($_.FullName)" -ForegroundColor Green }

Write-Host "
3. Buscando dentro del codigo Python por clases Agent..." -ForegroundColor Yellow
Get-ChildItem -Recurse -Filter "*.py" | Select-String -Pattern "class.*Agent" | ForEach-Object { Write-Host "  $($_.Filename): $($_.Line.Trim())" -ForegroundColor Green }

Write-Host "
4. Buscando carpetas de modulos..." -ForegroundColor Yellow
Get-ChildItem -Recurse -Directory | Where-Object { $_.Name -match "agent|module|financial|marketing|legal|collections|logistics" } | ForEach-Object { Write-Host "  $($_.FullName)" -ForegroundColor Green }

Write-Host "
5. Contando archivos por carpetas importantes..." -ForegroundColor Yellow
$dirs = @("agents", "modules", "apps", "src", "api", "models", "services")
foreach ($dir in $dirs) {
    if (Test-Path $dir) {
        $count = (Get-ChildItem -Path $dir -Recurse -File).Count
        Write-Host "  $dir/: $count archivos" -ForegroundColor Green
    }
}

Write-Host "
6. Buscando archivos de configuracion de agentes..." -ForegroundColor Yellow
Get-ChildItem -Recurse -Filter "*.json" | Where-Object { $_.Name -match "agent|config|registry" } | ForEach-Object { Write-Host "  $($_.Name)" -ForegroundColor Green }

Write-Host "
7. Analizando main.py y app.py..." -ForegroundColor Yellow
if (Test-Path "app.py") {
    $appContent = Get-Content "app.py" -Raw
    $agentImports = [regex]::Matches($appContent, "import.*[Aa]gent|from.*[Aa]gent").Count
    Write-Host "  app.py: $agentImports imports de agentes detectados" -ForegroundColor Green
}
if (Test-Path "main.py") {
    $mainContent = Get-Content "main.py" -Raw  
    $agentImports = [regex]::Matches($mainContent, "import.*[Aa]gent|from.*[Aa]gent").Count
    Write-Host "  main.py: $agentImports imports de agentes detectados" -ForegroundColor Green
}

Write-Host "
=== BUSQUEDA COMPLETADA ===" -ForegroundColor Cyan
