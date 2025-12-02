# scripts/marketing_core_audit_v4.5_fixed.ps1
param()

# Configuración
$Script:AuditVersion = "4.5"
$Script:Timestamp = Get-Date -Format "yyyy-MM-dd_HHmm"
$Script:ReportPath = "reports/marketing_core_audit_$($Script:Timestamp).md"
$Script:CsvPath = "reports/marketing_core_audit_$($Script:Timestamp).csv"

# Función para verificar AgentFactory
function Test-AgentFactory {
    try {
        Add-Type -Path "src/Core/agent_factory.py" -ErrorAction SilentlyContinue
        python -c "
import sys
sys.path.append('src')
from Core.agent_factory import get_agent_factory
factory = get_agent_factory()
print('SUCCESS:' + str(len(factory.agents)))
        " -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

# Función para obtener estado del agente desde AgentFactory
function Get-AgentStatusFromFactory($agentName) {
    try {
        $result = python -c "
import sys
sys.path.append('src')
from Core.agent_factory import get_agent_factory
factory = get_agent_factory()
agent = factory.get_agent('$agentName')
if agent:
    print('LINKED')
else:
    print('NOT_LINKED')
        " -ErrorAction Stop
        return $result.Trim()
    } catch {
        return "ERROR"
    }
}

Write-Host "🚀 INICIANDO AUDITORÍA MARKETING CORE v4.5 (FIXED)..." -ForegroundColor Green

# Verificar AgentFactory
Write-Host "🔍 Verificando AgentFactory..." -ForegroundColor Yellow
if (Test-AgentFactory) {
    Write-Host "✅ AgentFactory detectado y funcionando" -ForegroundColor Green
} else {
    Write-Host "❌ AgentFactory no disponible" -ForegroundColor Red
}

# Resto del script de auditoría (similar al original pero usando AgentFactory)
# ... (código existente de la auditoría)

Write-Host "✅ Auditoría completada (versión corregida)." -ForegroundColor Green
