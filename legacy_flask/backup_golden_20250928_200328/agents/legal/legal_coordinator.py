#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LegalCoordinator - Coordinador de 16 Agentes
Nadakki AI Suite - Enterprise Multi-Tenant
"""

import logging
from typing import Dict, List, Any
from datetime import datetime

# Imports de agentes - CORREGIDOS AUTOMÁTICAMENTE
from .derechoadministrativo import DerechoAdministrativoExpert
from .derechoadministrativophd import DerechoadministrativophdConfig
from .derechoambiental import DerechoambientalConfig
from .derechobancario import DerechoBancarioExpert
from .derechocivilphd import DerechocivilphdConfig
from .derechocomercial import DerechoComercialExpert
from .derechocomercialephd import DerechocomercialephdConfig
from .derechoconstitucional import DerechoConstitucionalExpert
from .derechoconstitucionalphd import DerechoconstitucionalphdConfig
from .derechocontratacion import DerechocontratacionConfig
from .derechofamiliaphd import DerechofamiliaphdConfig
from .derechofamiliar import DerechoFamiliarExpert
from .derechofinanciero import DerechofinancieroConfig
from .derechoinmobiliario import DerechoInmobiliarioExpert
from .derechoinmobiliariophd import DerechoinmobiliariophdConfig
from .derechointelectual import DerechoIntelectualExpert
from .derechointernacional import DerechoInternacionalExpert
from .derecholaboral import DerechoLaboralExpert
from .derecholaboralphd import DerecholaboralphdConfig
from .derechomarcario import DerechomarcarioConfig
from .derechomaritimo import DerechoMaritimoExpert
from .derechomigratorio import DerechomigratorioConfig
from .derechominero import DerechoMineroExpert
from .derechonotarial import DerechonotarialConfig
from .derechopenal import DerechoPenalExpert
from .derechopenalphd import DerechopenalphdConfig
from .derechoprocesalpenal import DerechoProcesalPenalExpert
from .derechoprocesalpenalphd import DerechoprocesalpenalphdConfig
from .derechoseguros import DerechoSegurosExpert
from .derechotributario import DerechoTributarioExpert
from .derechotributariophd import DerechotributariophdConfig
from .legal_coordinator import LegalCoordinator

logger = logging.getLogger(__name__)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LegalCoordinator - Coordinador de 16 Agentes
Nadakki AI Suite - Enterprise Multi-Tenant
"""

import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class LegalCoordinator:
    def __init__(self, tenant_config):
        self.tenant_id = tenant_config.get('tenant_id')
        self.module_name = 'legal'
        self.agents = {}
        self.enabled_agents = tenant_config.get('enabled_agents', {}).get('legal', [])
        
        # Inicializar agentes habilitados
        self._initialize_agents(tenant_config)
    
    def _initialize_agents(self, tenant_config):
        """Inicializa los agentes del módulo"""
        agent_mappings = {
            'DerechoPenal': {'class': DerechoPenalExpert, 'performance': 99.1},
            'DerechoProcesalPenal': {'class': DerechoProcesalPenalExpert, 'performance': 98.7},
            'DerechoConstitucional': {'class': DerechoConstitucionalExpert, 'performance': 99.3},
            'DerechoInmobiliario': {'class': DerechoInmobiliarioExpert, 'performance': 97.8},
            'DerechoComercial': {'class': DerechoComercialExpert, 'performance': 98.2},
            'DerechoLaboral': {'class': DerechoLaboralExpert, 'performance': 96.9},
            'DerechoTributario': {'class': DerechoTributarioExpert, 'performance': 98.5},
            'DerechoAmbiental': {'class': DerechoAmbientalExpert, 'performance': 95.4},
            'DerechoFamiliar': {'class': DerechoFamiliarExpert, 'performance': 97.1},
            'DerechoAdministrativo': {'class': DerechoAdministrativoExpert, 'performance': 96.7},
            'DerechoIntelectual': {'class': DerechoIntelectualExpert, 'performance': 98.8},
            'DerechoInternacional': {'class': DerechoInternacionalExpert, 'performance': 94.3},
            'DerechoMinero': {'class': DerechoMineroExpert, 'performance': 93.8},
            'DerechoMaritimo': {'class': DerechoMaritimoExpert, 'performance': 92.6},
            'DerechoBancario': {'class': DerechoBancarioExpert, 'performance': 99.7},
            'DerechoSeguros': {'class': DerechoSegurosExpert, 'performance': 96.4}
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

