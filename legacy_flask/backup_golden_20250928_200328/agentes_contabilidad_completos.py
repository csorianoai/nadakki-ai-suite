from agents.contabilidad.contabilidad_coordinator import ContabilidadCoordinator

class AccountingOrchestrator:
    def __init__(self):
        config = {
            'tenant_id': 'demo',
            'enabled_agents': {
                'contabilidad': [
                    'ConciliacionBancaria',
                    'CierreContable',
                    'DetectaAnomalias',
                    'ReporteFinanciero',
                    'AuditoriaInterna',
                    'FlujoCajaPrediccion'
                ]
            }
        }
        self.module = ContabilidadCoordinator(config)
    
    async def run_all(self, data):
        return self.module.execute_all_agents(data)
    
    async def get_accounting_health(self):
        return self.module.get_module_status()
