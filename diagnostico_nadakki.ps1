Write-Host "=== Diagnostico Nadakki AI Suite ===" -ForegroundColor Cyan
Write-Host "-------------------------------------`n"

# Backend
$appPath = ".\app.py"
if (Test-Path $appPath) {
  Write-Host "Backend (app.py): OK" -ForegroundColor Green
} else {
  Write-Host "Backend (app.py): NO DETECTADO" -ForegroundColor Red
}

# Entorno virtual
$envPath = ".\nadakki_env_clean\Scripts\Activate.ps1"
if (Test-Path $envPath) {
  Write-Host "Entorno virtual: OK" -ForegroundColor Green
} else {
  Write-Host "Entorno virtual: NO DETECTADO" -ForegroundColor Yellow
}

# Tenants
$tenantFolder = "public/config/tenants"
if (Test-Path $tenantFolder) {
  $tenants = Get-ChildItem $tenantFolder -Filter *.json | Where-Object { $_.Name -ne "tenants_index.json" }
  $count = $tenants.Count
  Write-Host "`nTenants encontrados: $count"
  foreach ($t in $tenants) {
    Write-Host " - $($t.Name)"
  }
} else {
  Write-Host "Carpeta tenants: NO ENCONTRADA" -ForegroundColor Red
}

# Planes
$agentsFile = "public/assets/agents_by_plan.json"
if (Test-Path $agentsFile) {
  $plans = Get-Content $agentsFile | ConvertFrom-Json
  Write-Host "`nPlanes configurados:"
  foreach ($p in $plans.PSObject.Properties.Name) {
    $total = $plans.$p.total_agents
    Write-Host " - $p ($total agentes)"
  }
} else {
  Write-Host "agents_by_plan.json: NO ENCONTRADO" -ForegroundColor Red
}

# Logs
if (Test-Path "logs/tenants.log") {
  $last = Get-Content logs/tenants.log | Select-Object -Last 3
  Write-Host "`nUltimos logs:"
  $last | ForEach-Object { Write-Host "   $_" }
} else {
  Write-Host "Archivo logs/tenants.log no encontrado" -ForegroundColor Yellow
}

# Recomendaciones
Write-Host "`nSugerencias:"
if ($count -eq 0) {
  Write-Host " - Crear al menos un tenant con crear_tenant.ps1"
}
if (-not (Test-Path $envPath)) {
  Write-Host " - Activar entorno virtual con .\\nadakki_env_clean\\Scripts\\Activate.ps1"
}
if (-not (Test-Path $agentsFile)) {
  Write-Host " - Definir planes en agents_by_plan.json"
}
if (($count -gt 0) -and (Test-Path $agentsFile)) {
  Write-Host " - Probar carga frontend: index.html?tenant=<nombre>"
  Write-Host " - Validar agentes desde la interfaz"
}

Write-Host "`nDiagnostico completado."
