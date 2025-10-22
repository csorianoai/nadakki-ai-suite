Write-Host "=== ANALISIS PROFUNDO CARPETA AGENTS ===" -ForegroundColor Cyan

Write-Host "Contando archivos por subcarpeta en agents/:" -ForegroundColor Yellow
Get-ChildItem agents -Directory | ForEach-Object {
    $count = (Get-ChildItem $_.FullName -File -Recurse).Count
    Write-Host "  $($_.Name): $count archivos" -ForegroundColor Green
}

Write-Host "
Listando coordinadores y sus archivos:" -ForegroundColor Yellow
Get-ChildItem -Filter "*coordinator.py" | ForEach-Object {
    Write-Host "  $($_.Name)" -ForegroundColor Green
}

Write-Host "
Analizando archivos de configuracion JSON:" -ForegroundColor Yellow
Get-ChildItem -Filter "*_config.json" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw | ConvertFrom-Json
    if ($content.agents) {
        Write-Host "  $($_.Name): $($content.agents.Count) agentes configurados" -ForegroundColor Green
    }
}

Write-Host "
Buscando archivos principales de agentes individuales:" -ForegroundColor Yellow
Get-ChildItem agents -Recurse -Filter "*.py" | Where-Object { $_.Name -notmatch "coordinator|__" } | Select-Object -First 20 | ForEach-Object {
    Write-Host "  $($_.FullName.Replace((Get-Location), '.'))" -ForegroundColor White
}
