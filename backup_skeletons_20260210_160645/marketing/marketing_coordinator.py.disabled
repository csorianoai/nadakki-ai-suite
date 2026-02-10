#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MarketingCoordinator - Coordinador de 14 Agentes
Nadakki AI Suite - Enterprise Multi-Tenant
"""

import logging
from typing import Dict, List, Any
from datetime import datetime

# Imports de agentes - CORREGIDOS AUTOMÁTICAMENTE
from .abtestingimpactia import AbtestingimpactiaConfig
from .brandsentimentia import BrandsentimentiaConfig
from .campaignoptimizeria import CampaignOptimizer
from .cashofferfilteria import CashofferfilteriaConfig
from .competitorintelligenceia import CompetitorintelligenceiaConfig
from .contactqualityia import ContactqualityiaConfig
from .contentviralityia import ContentviralityiaConfig
from .conversioncohortia import ConversioncohortiaConfig
from .emailautomationia import EmailAutomationEngine
from .fidelizedprofileia import FidelizedprofileiaConfig
from .geosegmentationia import GeosegmentationiaConfig
from .influencermatcheria import InfluencerMatcher
from .influencermatchia import InfluencermatchiaConfig
from .leadscoringia import LeadScoringEngine
from .marketing_coordinator import MarketingCoordinator
from .minimalformia import MinimalformiaConfig
from .productaffinityia import ProductaffinityiaConfig
from .socialpostgeneratoria import SocialpostgeneratoriaConfig
from .videoreelautogenia import VideoreelautogeniaConfig

logger = logging.getLogger(__name__)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MarketingCoordinator - Coordinador de 14 Agentes
Nadakki AI Suite - Enterprise Multi-Tenant
"""

import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class MarketingCoordinator:
    def __init__(self, tenant_config):
        self.tenant_id = tenant_config.get('tenant_id')
        self.module_name = 'marketing'
        self.agents = {}
        self.enabled_agents = tenant_config.get('enabled_agents', {}).get('marketing', [])
        
        # Inicializar agentes habilitados
        self._initialize_agents(tenant_config)
    
    def _initialize_agents(self, tenant_config):
        """Inicializa los agentes del módulo"""
        agent_mappings = {
            'MinimalFormIA': {'class': MinimalFormOptimizer, 'performance': 89.3},
            'FidelizedProfileIA': {'class': FidelizationProfiler, 'performance': 91.7},
            'CashOfferFilterIA': {'class': CashOfferOptimizer, 'performance': 87.2},
            'ContactQualityIA': {'class': ContactQualityAnalyzer, 'performance': 94.1},
            'GeoSegmentationIA': {'class': GeoSegmentationEngine, 'performance': 92.8},
            'ProductAffinityIA': {'class': ProductAffinityPredictor, 'performance': 88.6},
            'ConversionCohortIA': {'class': ConversionCohortAnalyzer, 'performance': 90.4},
            'ABTestingImpactIA': {'class': ABTestingEngine, 'performance': 93.7},
            'SocialPostGeneratorIA': {'class': SocialContentGenerator, 'performance': 85.9},
            'VideoReelAutogenIA': {'class': VideoContentGenerator, 'performance': 82.3},
            'InfluencerMatcherIA': {'class': InfluencerMatcher, 'performance': 86.7},
            'CampaignOptimizerIA': {'class': CampaignOptimizer, 'performance': 91.2},
            'LeadScoringIA': {'class': LeadScoringEngine, 'performance': 89.8},
            'EmailAutomationIA': {'class': EmailAutomationEngine, 'performance': 87.4}
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

