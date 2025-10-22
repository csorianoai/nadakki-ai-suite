Write-Host "=== CONTEO REAL DE AGENTES POR MODULO ===" -ForegroundColor Cyan

$modules = @('compliance', 'contabilidad', 'decision', 'educacion', 'experiencia', 'fortaleza', 'inteligencia', 'investigacion', 'legal', 'logistica', 'marketing', 'operacional', 'originacion', 'presupuesto', 'recuperacion', 'regtech', 'rrhh', 'ventascrm', 'vigilancia')

foreach ($module in $modules) {
    if (Test-Path "agents/$module") {
        $agentFiles = Get-ChildItem "agents/$module" -Filter "*.py" | Where-Object { $_.Name -notmatch "coordinator|__init__|config" }
        Write-Host "
$module.ToUpper(): $($agentFiles.Count) agentes" -ForegroundColor Yellow
        $agentFiles | Select-Object -First 10 | ForEach-Object {
            Write-Host "  - $($_.BaseName)" -ForegroundColor Green
        }
        if ($agentFiles.Count -gt 10) {
            Write-Host "  ... y $($agentFiles.Count - 10) agentes más" -ForegroundColor Gray
        }
    }
}

$totalAgents = 0
foreach ($module in $modules) {
    if (Test-Path "agents/$module") {
        $count = (Get-ChildItem "agents/$module" -Filter "*.py" | Where-Object { $_.Name -notmatch "coordinator|__init__|config" }).Count
        $totalAgents += $count
    }
}

Write-Host "
=== RESUMEN TOTAL ===" -ForegroundColor Cyan
Write-Host "TOTAL DE AGENTES IMPLEMENTADOS: $totalAgents" -ForegroundColor Magenta
