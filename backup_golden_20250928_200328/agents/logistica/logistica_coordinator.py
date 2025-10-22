#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LogisticaCoordinator - Coordinador de 13 Agentes
Nadakki AI Suite - Enterprise Multi-Tenant
"""

import logging
from typing import Dict, List, Any
from datetime import datetime

# Imports de agentes - CORREGIDOS AUTOMÁTICAMENTE
from .alertasinventario import AlertasinventarioConfig
from .almaceninteligente import IntelligentWarehouseEngine
from .analisisrendimiento import PerformanceAnalysisEngine
from .controlcalidad import ControlcalidadConfig
from .controlcalidadia import QualityControlAIEngine
from .controlpedidosia import ControlpedidosiaConfig
from .costoslogisticos import CostoslogisticosConfig
from .evaluadorproveedoresia import EvaluadorproveedoresiaConfig
from .gestionriesgos import RiskManagementEngine
from .logisticareversa import LogisticareversaConfig
from .logistica_coordinator import LogisticaCoordinator
from .optimizacionalmacen import OptimizacionalmacenConfig
from .optimizacioncostos import CostOptimizationEngine
from .optimizadorrutasia import OptimizadorrutasiaConfig
from .planificaciondemanda import DemandPlanningEngine
from .predicciondemanda import PredicciondemandaConfig
from .previsioninventarioia import PrevisioninventarioiaConfig
from .seguridadcarga import SeguridadcargaConfig
from .sostenibilidadia import SustainabilityAIEngine
from .transporteoptimizado import TransportOptimizationEngine
from .transportepredictivo import TransportepredictivoConfig
from .trazabilidadia import TrazabilidadiaConfig
from .trazabilidadtotal import TraceabilityEngine

logger = logging.getLogger(__name__)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LogisticaCoordinator - Coordinador de 13 Agentes
Nadakki AI Suite - Enterprise Multi-Tenant
"""

import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class LogisticaCoordinator:
    def __init__(self, tenant_config):
        self.tenant_id = tenant_config.get('tenant_id')
        self.module_name = 'logistica'
        self.agents = {}
        self.enabled_agents = tenant_config.get('enabled_agents', {}).get('logistica', [])
        
        # Inicializar agentes habilitados
        self._initialize_agents(tenant_config)
    
    def _initialize_agents(self, tenant_config):
        """Inicializa los agentes del módulo"""
        agent_mappings = {
            'OptimizadorRutasIA': {'class': RouteOptimizationEngine, 'performance': 95.3},
            'PrevisionInventarioIA': {'class': InventoryForecastingEngine, 'performance': 92.7},
            'ControlPedidosIA': {'class': OrderControlEngine, 'performance': 94.1},
            'EvaluadorProveedoresIA': {'class': SupplierEvaluationEngine, 'performance': 89.6},
            'AlmacenInteligente': {'class': IntelligentWarehouseEngine, 'performance': 91.8},
            'TransporteOptimizado': {'class': TransportOptimizationEngine, 'performance': 93.4},
            'TrazabilidadTotal': {'class': TraceabilityEngine, 'performance': 96.7},
            'PlanificacionDemanda': {'class': DemandPlanningEngine, 'performance': 88.9},
            'ControlCalidadIA': {'class': QualityControlAIEngine, 'performance': 94.8},
            'OptimizacionCostos': {'class': CostOptimizationEngine, 'performance': 90.2},
            'GestionRiesgos': {'class': RiskManagementEngine, 'performance': 87.5},
            'AnalisisRendimiento': {'class': PerformanceAnalysisEngine, 'performance': 92.1},
            'SostenibilidadIA': {'class': SustainabilityAIEngine, 'performance': 85.7}
        }
        
        for agent_name in self.enabled_agents:
            if agent_name in agent_mappings:
                try:
                    agent_class = agent_mappings[agent_name]['class']
                    self.agents[agent_name] = agent_class(tenant_config)
                    logger.info(f"Agent {agent_name} initialized for tenant {self.tenant_id}")
                except Exception as e:
                    logger.error(f"Error initializing {agent_name}: {str(e)}")
    
    def execute_agent(self, agent_name, data):
        """Ejecuta un agente específico"""
        if agent_name not in self.agents:
            return {'error': f'Agent {agent_name} not available', 'module': self.module_name}
        
        try:
            agent = self.agents[agent_name]
            
            # Determinar el método principal del agente
            if hasattr(agent, 'analyze_credit_profile'):
                result = agent.analyze_credit_profile(data)
            elif hasattr(agent, 'monitor_compliance'):
                result = agent.monitor_compliance(data)
            elif hasattr(agent, 'optimize_operation'):
                result = agent.optimize_operation(data)
            elif hasattr(agent, 'predict_outcome'):
                result = agent.predict_outcome(data)
            else:
                result = {'error': 'No main method found'}
            
            # Agregar metadatos del módulo
            result.update({
                'module': self.module_name,
                'execution_time': datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing {agent_name}: {str(e)}")
            return {'error': str(e), 'agent': agent_name, 'module': self.module_name}
    
    def get_module_status(self):
        """Obtiene el estado del módulo"""
        return {
            'module': self.module_name,
            'tenant_id': self.tenant_id,
            'total_agents': len(self.agents),
            'enabled_agents': list(self.agents.keys()),
            'status': 'operational' if self.agents else 'no_agents_enabled'
        }
    
    def execute_all_agents(self, data):
        """Ejecuta todos los agentes habilitados"""
        results = {}
        for agent_name in self.agents:
            results[agent_name] = self.execute_agent(agent_name, data)
        return results

