Write-Host "ACTUALIZANDO DASHBOARD CREDICEFI CON DISEÑO FUTURISTA..." -ForegroundColor Cyan

# Leer la plantilla futurista
$nuevoDashboard = Get-Content -Raw -Path "dashboards\template_futurista.html"

# Actualizar el dashboard de Credicefi
$dashboardPath = "dashboards\credicefi_b27fa331_dashboard.html"

if (Test-Path $dashboardPath) {
    try {
        # Crear backup
        $backupPath = "$dashboardPath.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        Copy-Item $dashboardPath $backupPath
        Write-Host "Backup creado: $(Split-Path $backupPath -Leaf)" -ForegroundColor Yellow
        
        # Reemplazar con nuevo diseño
        $nuevoDashboard | Set-Content -Path $dashboardPath -Encoding UTF8
        Write-Host "Dashboard actualizado exitosamente!" -ForegroundColor Green
        
        # Abrir el dashboard actualizado
        Start-Process $dashboardPath
        Write-Host "Dashboard abierto en navegador" -ForegroundColor Green
        
    } catch {
        Write-Host "Error al actualizar: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "No se encontró el dashboard de Credicefi" -ForegroundColor Red
}
