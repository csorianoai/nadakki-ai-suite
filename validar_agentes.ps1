Write-Host "🔍 Mostrando contenido de SentinelBot..."
Get-Content agents\originacion\sentinelbot.py | Select-Object -First 30

Write-Host "🧪 Ejecutando pruebas unitarias..."
pytest agents/ --maxfail=5 --disable-warnings -q

Write-Host "📂 Abriendo coordinator.py para revisión..."
Start-Process notepad.exe coordinator.py
Pause

Write-Host "📂 Abriendo configuración del tenant Banreservas..."
Start-Process notepad.exe config\tenants\banreservas.json
Pause

Write-Host "🌐 Verificando agentes expuestos para Banreservas..."
curl -H "X-Tenant-ID: banreservas" http://localhost:5000/api/agents
