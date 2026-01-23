# ═══════════════════════════════════════════════════════════════════════════════
# CONVERSIÓN MASIVA DE AGENTES A OPERATIVOS
# ═══════════════════════════════════════════════════════════════════════════════

$template = @"
def execute_operative(self, context: OperativeContext) -> OperativeResult:
    \"\"\"
    Execute operative actions for {agent_name}
    \"\"\"
    try:
        # 1. Validar contexto
        if not context.tenant_id:
            raise ValueError("tenant_id is required")
            
        # 2. Obtener configuración del tenant
        config = self.get_tenant_config(context.tenant_id)
        
        # 3. Ejecutar lógica específica del agente
        result = self.execute(context)
        
        # 4. Registrar en sistema operativo
        operative_log = {
            "agent": "{agent_name}",
            "tenant_id": context.tenant_id,
            "timestamp": datetime.now().isoformat(),
            "result": result
        }
        
        # 5. Retornar resultado estandarizado
        return OperativeResult(
            success=True,
            data=result,
            operative_log=operative_log
        )
        
    except Exception as e:
        logger.error(f"Operative execution failed: {str(e)}")
        return OperativeResult(
            success=False,
            error=str(e)
        )
"@

# Aplicar a cada agente
foreach ($agent in $agents) {
    $content = Get-Content $agent.FullName -Raw
    $newContent = $content -replace "def execute\(self.*?\):", "$&`n`n    " + ($template -replace "{agent_name}", $agent.BaseName)
    Set-Content -Path $agent.FullName -Value $newContent -Encoding UTF8
    Write-Host "✅ Convertido: $($agent.BaseName)" -ForegroundColor Green
}
