"""
NADAKKI AI SUITE - HYPER MARKETING BRIDGE
Integra los 35 agentes de marketing existentes con las capacidades de hyper_agents.

CARACTERÍSTICAS:
- Cada agente de marketing obtiene: pensamiento paralelo, memoria, RL, budget, safety
- Mantiene compatibilidad con la API existente
- Multi-tenant nativo
- Trazabilidad completa
"""

import asyncio
import json
import importlib
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field

# Importar módulo hyper_agents
from hyper_agents.core import (
    HyperCortex, MemoryType, ActionType, ActionDef,
    SafetyLevel, EthicalAssessment
)
from hyper_agents.memory import QuantumMemory
from hyper_agents.learning import RLLearningEngine
from hyper_agents.budget import BudgetManager
from hyper_agents.safety import SafetyFilter


# ============================================================================
# LISTA DE 35 AGENTES DE MARKETING
# ============================================================================

MARKETING_AGENTS = [
    # Lead Management (3)
    {"id": "leadscoria", "name": "LeadScorIA", "category": "lead_management"},
    {"id": "leadscoringia", "name": "LeadScoringIA", "category": "lead_management"},
    {"id": "predictiveleadia", "name": "PredictiveLeadIA", "category": "lead_management"},
    
    # Experimentation (2)
    {"id": "abtestingia", "name": "ABTestingIA", "category": "experimentation"},
    {"id": "abtestingimpactia", "name": "ABTestingImpactIA", "category": "experimentation"},
    
    # Campaign Management (2)
    {"id": "campaignoptimizeria", "name": "CampaignOptimizerIA", "category": "campaign"},
    {"id": "marketingorchestratorea", "name": "MarketingOrchestratorEA", "category": "campaign"},
    
    # Content (3)
    {"id": "contentgeneratoria", "name": "ContentGeneratorIA", "category": "content"},
    {"id": "contentperformanceia", "name": "ContentPerformanceIA", "category": "content"},
    {"id": "socialpostgeneratoria", "name": "SocialPostGeneratorIA", "category": "content"},
    
    # Analytics (4)
    {"id": "sentimentanalyzeria", "name": "SentimentAnalyzerIA", "category": "analytics"},
    {"id": "sociallisteningia", "name": "SocialListeningIA", "category": "analytics"},
    {"id": "conversioncohortia", "name": "ConversionCohortIA", "category": "analytics"},
    {"id": "channelattributia", "name": "ChannelAttributIA", "category": "analytics"},
    
    # Competitive Intelligence (2)
    {"id": "competitoranalyzeria", "name": "CompetitorAnalyzerIA", "category": "competitive"},
    {"id": "competitorintelligenceia", "name": "CompetitorIntelligenceIA", "category": "competitive"},
    
    # Attribution (2)
    {"id": "attributionmodelia", "name": "AttributionModelIA", "category": "attribution"},
    {"id": "marketingmixmodelia", "name": "MarketingMixModelIA", "category": "attribution"},
    
    # Forecasting (1)
    {"id": "budgetforecastia", "name": "BudgetForecastIA", "category": "forecasting"},
    
    # Segmentation (3)
    {"id": "audiencesegmenteria", "name": "AudienceSegmenterIA", "category": "segmentation"},
    {"id": "customersegmentatonia", "name": "CustomerSegmentationIA", "category": "segmentation"},
    {"id": "geosegmentationia", "name": "GeoSegmentationIA", "category": "segmentation"},
    
    # Personalization (2)
    {"id": "personalizationengineia", "name": "PersonalizationEngineIA", "category": "personalization"},
    {"id": "productaffinityia", "name": "ProductAffinityIA", "category": "personalization"},
    
    # Email (1)
    {"id": "emailautomationia", "name": "EmailAutomationIA", "category": "email"},
    
    # Influencer (2)
    {"id": "influencermatcheria", "name": "InfluencerMatcherIA", "category": "influencer"},
    {"id": "influencermatchingia", "name": "InfluencerMatchingIA", "category": "influencer"},
    
    # Customer Journey (2)
    {"id": "journeyoptimizeria", "name": "JourneyOptimizerIA", "category": "journey"},
    {"id": "retentionpredictoria", "name": "RetentionPredictorIA", "category": "journey"},
    {"id": "retentionpredictorea", "name": "RetentionPredictorEA", "category": "journey"},
    
    # Pricing (1)
    {"id": "pricingoptimizeria", "name": "PricingOptimizerIA", "category": "pricing"},
    
    # Creative (1)
    {"id": "creativeanalyzeria", "name": "CreativeAnalyzerIA", "category": "creative"},
    
    # Data Quality (1)
    {"id": "contactqualityia", "name": "ContactQualityIA", "category": "data_quality"},
    
    # Offers (1)
    {"id": "cashofferfilteria", "name": "CashOfferFilterIA", "category": "offers"},
    
    # Forms (1)
    {"id": "minimalformia", "name": "MinimalFormIA", "category": "forms"},
]


# ============================================================================
# HYPER EXECUTION RESULT
# ============================================================================

@dataclass
class HyperExecutionResult:
    """Resultado de ejecución con capacidades hyper"""
    success: bool
    agent_id: str
    agent_name: str
    tenant_id: str
    
    # Resultado del agente original
    original_result: Dict[str, Any] = field(default_factory=dict)
    
    # Capacidades Hyper
    parallel_thoughts: Optional[Dict[str, Any]] = None
    ethical_assessment: Optional[Dict[str, Any]] = None
    safety_check: Optional[Dict[str, Any]] = None
    memory_context: List[Dict] = field(default_factory=list)
    
    # Learning
    rl_update: Optional[Dict[str, Any]] = None
    learnings: List[str] = field(default_factory=list)
    
    # Metrics
    execution_time_ms: float = 0.0
    cost_usd: float = 0.0
    budget_status: Optional[Dict[str, Any]] = None
    
    # Meta
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "tenant_id": self.tenant_id,
            "original_result": self.original_result,
            "hyper_features": {
                "parallel_thoughts": self.parallel_thoughts,
                "ethical_assessment": self.ethical_assessment,
                "safety_check": self.safety_check,
                "memory_context_count": len(self.memory_context)
            },
            "learning": {
                "rl_update": self.rl_update,
                "learnings": self.learnings
            },
            "metrics": {
                "execution_time_ms": self.execution_time_ms,
                "cost_usd": round(self.cost_usd, 6),
                "budget_status": self.budget_status
            },
            "timestamp": self.timestamp,
            "error": self.error,
            "warnings": self.warnings
        }


# ============================================================================
# HYPER MARKETING BRIDGE
# ============================================================================

class HyperMarketingBridge:
    """
    Bridge que integra los 35 agentes de marketing con capacidades hyper.
    
    CICLO DE EJECUCIÓN:
    1. Verificar presupuesto
    2. Recuperar contexto de memoria
    3. Pensamiento paralelo (análisis previo)
    4. Evaluación ética
    5. Ejecutar agente original
    6. Verificar seguridad del output
    7. Actualizar RL
    8. Guardar en memoria
    """
    
    def __init__(self, tenant_id: str = "default"):
        self.tenant_id = tenant_id
        
        # Componentes Hyper (compartidos por todos los agentes del tenant)
        self.cortex = HyperCortex(agent_id="marketing_bridge", tenant_id=tenant_id)
        self.memory = QuantumMemory(tenant_id=tenant_id, agent_id="marketing_shared")
        self.rl_engine = RLLearningEngine(agent_id="marketing_bridge", tenant_id=tenant_id)
        self.budget_manager = BudgetManager(tenant_id=tenant_id, monthly_budget_usd=100.0)
        self.safety_filter = SafetyFilter(tenant_id=tenant_id, strictness=0.7)
        
        # Cache de módulos de agentes
        self._agent_modules: Dict[str, Any] = {}
        
        # Estadísticas
        self.stats = {
            "total_executions": 0,
            "by_agent": {},
            "by_category": {},
            "total_cost": 0.0
        }
        
        print(f"🚀 HyperMarketingBridge inicializado para tenant: {tenant_id}")
        print(f"   35 agentes de marketing disponibles con capacidades hyper")
    
    def get_available_agents(self) -> List[Dict[str, str]]:
        """Retorna lista de agentes disponibles"""
        return MARKETING_AGENTS.copy()
    
    def get_agents_by_category(self, category: str) -> List[Dict[str, str]]:
        """Retorna agentes filtrados por categoría"""
        return [a for a in MARKETING_AGENTS if a["category"] == category]
    
    async def execute(
        self,
        agent_id: str,
        input_data: Dict[str, Any],
        options: Dict[str, Any] = None
    ) -> HyperExecutionResult:
        """
        Ejecuta un agente de marketing con capacidades hyper.
        
        Args:
            agent_id: ID del agente (ej: "socialpostgeneratoria")
            input_data: Datos de entrada para el agente
            options: Opciones adicionales (skip_parallel, skip_safety, etc.)
        
        Returns:
            HyperExecutionResult con resultado completo
        """
        start_time = datetime.utcnow()
        options = options or {}
        
        # Buscar info del agente
        agent_info = next((a for a in MARKETING_AGENTS if a["id"] == agent_id), None)
        if not agent_info:
            return HyperExecutionResult(
                success=False,
                agent_id=agent_id,
                agent_name="Unknown",
                tenant_id=self.tenant_id,
                error=f"Agente no encontrado: {agent_id}"
            )
        
        result = HyperExecutionResult(
            success=False,
            agent_id=agent_id,
            agent_name=agent_info["name"],
            tenant_id=self.tenant_id
        )
        
        try:
            # ─────────────────────────────────────────────────────────────
            # PASO 1: Verificar presupuesto
            # ─────────────────────────────────────────────────────────────
            result.budget_status = self.budget_manager.get_budget_status()
            can_execute, reason = self.budget_manager.can_execute(0.01)
            
            if not can_execute:
                result.warnings.append(f"Budget warning: {reason}")
            
            # ─────────────────────────────────────────────────────────────
            # PASO 2: Recuperar contexto de memoria
            # ─────────────────────────────────────────────────────────────
            query = f"{agent_id} {json.dumps(input_data, ensure_ascii=False)[:200]}"
            result.memory_context = await self.memory.get_context(
                query=query,
                limit=5,
                tags=[agent_info["category"], agent_id]
            )
            
            # ─────────────────────────────────────────────────────────────
            # PASO 3: Pensamiento paralelo (si no está deshabilitado)
            # ─────────────────────────────────────────────────────────────
            if not options.get("skip_parallel", False):
                parallel_result = await self.cortex.parallel_think(
                    query=f"Analizar input para {agent_info['name']}: {query[:300]}",
                    context={"agent": agent_id, "category": agent_info["category"]},
                    num_streams=2  # Reducido para performance
                )
                result.parallel_thoughts = {
                    "consensus_level": parallel_result.get("consensus_level", 0),
                    "recommended_action": parallel_result.get("recommended_action", ""),
                    "streams_count": len(parallel_result.get("streams", []))
                }
            
            # ─────────────────────────────────────────────────────────────
            # PASO 4: Evaluación ética
            # ─────────────────────────────────────────────────────────────
            if not options.get("skip_ethics", False):
                ethical_result = await self.cortex.ethical_assessment({
                    "agent": agent_id,
                    "input": input_data,
                    "category": agent_info["category"]
                })
                result.ethical_assessment = {
                    "score": ethical_result.overall_score,
                    "recommendation": ethical_result.recommendation,
                    "concerns": ethical_result.concerns
                }
                
                if ethical_result.recommendation == "REJECT":
                    result.error = "Rechazado por evaluación ética"
                    result.warnings.extend(ethical_result.concerns)
                    return result
            
            # ─────────────────────────────────────────────────────────────
            # PASO 5: Ejecutar agente original
            # ─────────────────────────────────────────────────────────────
            original_result = await self._execute_original_agent(
                agent_id=agent_id,
                input_data=input_data,
                context={
                    "tenant_id": self.tenant_id,
                    "memory_context": result.memory_context,
                    "parallel_consensus": result.parallel_thoughts.get("consensus_level", 0) if result.parallel_thoughts else 0
                }
            )
            result.original_result = original_result
            
            # ─────────────────────────────────────────────────────────────
            # PASO 6: Verificar seguridad del output
            # ─────────────────────────────────────────────────────────────
            if not options.get("skip_safety", False):
                # Extraer contenido a verificar
                content_to_check = self._extract_content_for_safety(original_result)
                
                if content_to_check:
                    safety_result = self.safety_filter.check_content(
                        content=content_to_check,
                        content_type=agent_info["category"],
                        agent_id=agent_id
                    )
                    result.safety_check = {
                        "is_safe": safety_result.is_safe,
                        "level": safety_result.safety_level.value,
                        "score": safety_result.score,
                        "issues": safety_result.issues
                    }
                    
                    if not safety_result.is_safe:
                        result.warnings.append(f"Safety issues: {safety_result.issues}")
            
            # ─────────────────────────────────────────────────────────────
            # PASO 7: Actualizar RL
            # ─────────────────────────────────────────────────────────────
            execution_success = original_result.get("status") == "success" or original_result.get("success", False)
            reward = 0.8 if execution_success else 0.3
            
            if result.parallel_thoughts:
                reward *= (0.5 + result.parallel_thoughts.get("consensus_level", 0.5))
            
            rl_update = self.rl_engine.update_policy(
                context=agent_info["category"],
                action=agent_id,
                success=execution_success,
                reward=reward,
                cost=result.cost_usd
            )
            result.rl_update = rl_update
            result.learnings.append(f"RL: reward={reward:.2f}, conf={rl_update.get('new_confidence', 0):.2f}")
            
            # ─────────────────────────────────────────────────────────────
            # PASO 8: Guardar en memoria
            # ─────────────────────────────────────────────────────────────
            await self.memory.store(
                key=f"{agent_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                content={
                    "agent_id": agent_id,
                    "input_summary": str(input_data)[:200],
                    "success": execution_success,
                    "reward": reward
                },
                memory_type=MemoryType.SHORT_TERM,
                importance=reward,
                tags=[agent_info["category"], agent_id, self.tenant_id]
            )
            
            result.success = True
            
        except Exception as e:
            result.success = False
            result.error = str(e)
            
            # Registrar fallo en RL
            self.rl_engine.update_policy(
                context=agent_info["category"],
                action=agent_id,
                success=False,
                reward=0.0
            )
        
        # Calcular tiempo y actualizar stats
        result.execution_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        self._update_stats(agent_id, agent_info["category"], result)
        
        return result
    
    async def _execute_original_agent(
        self,
        agent_id: str,
        input_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ejecuta el agente de marketing original.
        Intenta importar desde agents.marketing.{agent_id}
        """
        try:
            # Intentar cargar módulo si no está en cache
            if agent_id not in self._agent_modules:
                try:
                    module = importlib.import_module(f"agents.marketing.{agent_id}")
                    self._agent_modules[agent_id] = module
                except ImportError:
                    # Si no se puede importar, retornar resultado mock
                    return self._mock_agent_result(agent_id, input_data)
            
            module = self._agent_modules[agent_id]
            
            # Buscar función execute
            if hasattr(module, "execute"):
                # Preparar input con contexto
                enriched_input = {
                    "input_data": input_data,
                    **context
                }
                result = module.execute(enriched_input, context)
                return result if isinstance(result, dict) else {"result": result, "status": "success"}
            else:
                return self._mock_agent_result(agent_id, input_data)
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "agent_id": agent_id
            }
    
    def _mock_agent_result(self, agent_id: str, input_data: Dict) -> Dict[str, Any]:
        """Genera resultado mock para testing"""
        return {
            "status": "success",
            "agent_id": agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "result": {
                "score": 0.85,
                "confidence": 0.9,
                "recommendations": [f"Recommendation from {agent_id}"],
                "analysis": f"Analysis completed by {agent_id}"
            },
            "input_received": str(input_data)[:100],
            "_mock": True
        }
    
    def _extract_content_for_safety(self, result: Dict) -> Optional[str]:
        """Extrae contenido textual del resultado para verificar seguridad"""
        # Buscar campos comunes de contenido
        content_fields = ["content", "text", "message", "post", "email_body", "recommendation"]
        
        for field in content_fields:
            if field in result:
                return str(result[field])
            if "result" in result and isinstance(result["result"], dict):
                if field in result["result"]:
                    return str(result["result"][field])
        
        # Si no hay contenido específico, verificar el resultado completo
        return json.dumps(result, ensure_ascii=False)[:500]
    
    def _update_stats(self, agent_id: str, category: str, result: HyperExecutionResult):
        """Actualiza estadísticas internas"""
        self.stats["total_executions"] += 1
        
        if agent_id not in self.stats["by_agent"]:
            self.stats["by_agent"][agent_id] = {"executions": 0, "successes": 0}
        self.stats["by_agent"][agent_id]["executions"] += 1
        if result.success:
            self.stats["by_agent"][agent_id]["successes"] += 1
        
        if category not in self.stats["by_category"]:
            self.stats["by_category"][category] = {"executions": 0, "successes": 0}
        self.stats["by_category"][category]["executions"] += 1
        if result.success:
            self.stats["by_category"][category]["successes"] += 1
        
        self.stats["total_cost"] += result.cost_usd
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas completas"""
        return {
            "tenant_id": self.tenant_id,
            "total_executions": self.stats["total_executions"],
            "by_agent": self.stats["by_agent"],
            "by_category": self.stats["by_category"],
            "total_cost_usd": round(self.stats["total_cost"], 6),
            "budget_status": self.budget_manager.get_budget_status(),
            "rl_summary": self.rl_engine.get_learning_summary(),
            "memory_stats": self.memory.get_stats()
        }
    
    def get_best_agents(self, category: str = None, top_n: int = 5) -> List[Dict]:
        """Retorna los mejores agentes según RL"""
        context = category if category else "marketing"
        return self.rl_engine.get_best_actions(context, top_n)


# ============================================================================
# BATCH EXECUTION
# ============================================================================

async def execute_marketing_workflow(
    bridge: HyperMarketingBridge,
    workflow_steps: List[Dict[str, Any]]
) -> List[HyperExecutionResult]:
    """
    Ejecuta un workflow de marketing con múltiples agentes.
    
    Args:
        bridge: Instancia de HyperMarketingBridge
        workflow_steps: Lista de pasos [{agent_id, input_data, options}]
    
    Returns:
        Lista de resultados
    """
    results = []
    
    for step in workflow_steps:
        result = await bridge.execute(
            agent_id=step["agent_id"],
            input_data=step.get("input_data", {}),
            options=step.get("options", {})
        )
        results.append(result)
        
        # Si un paso falla y es crítico, detener
        if not result.success and step.get("critical", False):
            break
    
    return results


# ============================================================================
# TEST
# ============================================================================

async def test_hyper_marketing_bridge():
    """Test del bridge"""
    print("\n" + "=" * 70)
    print("  TEST: HYPER MARKETING BRIDGE")
    print("=" * 70)
    
    # Crear bridge
    bridge = HyperMarketingBridge(tenant_id="credicefi")
    
    # Listar agentes
    agents = bridge.get_available_agents()
    print(f"\n✅ Agentes disponibles: {len(agents)}")
    
    # Ejecutar algunos agentes
    test_agents = ["socialpostgeneratoria", "leadscoria", "sentimentanalyzeria"]
    
    for agent_id in test_agents:
        print(f"\n🔄 Ejecutando: {agent_id}")
        
        result = await bridge.execute(
            agent_id=agent_id,
            input_data={
                "topic": "Promoción de préstamos personales",
                "platform": "facebook",
                "tone": "profesional"
            }
        )
        
        print(f"   ✅ Success: {result.success}")
        print(f"   🧠 Consenso: {result.parallel_thoughts.get('consensus_level', 0):.2f}" if result.parallel_thoughts else "")
        print(f"   ⚖️ Ética: {result.ethical_assessment.get('score', 0):.2f}" if result.ethical_assessment else "")
        print(f"   ⏱️ Tiempo: {result.execution_time_ms:.0f}ms")
    
    # Stats finales
    print(f"\n📊 Stats finales:")
    stats = bridge.get_stats()
    print(f"   Total ejecuciones: {stats['total_executions']}")
    print(f"   Por categoría: {list(stats['by_category'].keys())}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(test_hyper_marketing_bridge())
