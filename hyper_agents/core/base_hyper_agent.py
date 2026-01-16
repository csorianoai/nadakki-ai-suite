"""
NADAKKI AI SUITE - BASE HYPER AGENT
Clase base independiente para Hyper Agentes nivel 0.1%
"""

import asyncio
import json
import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from .types import (
    ActionType, ActionDef, AutonomyLevel, MemoryType,
    HyperAgentProfile, HyperAgentOutput, EthicalAssessment
)
from .adapters import get_llm, BaseLLM
from .hyper_cortex import HyperCortex


class BaseHyperAgent(ABC):
    """Clase base para Hyper Agentes nivel 0.1%"""
    
    def __init__(self, profile: HyperAgentProfile):
        self.profile = profile
        self.llm: BaseLLM = get_llm()
        
        self._cortex: Optional[HyperCortex] = None
        self._memory = None
        self._rl_engine = None
        self._budget_manager = None
        self._safety_filter = None
        
        self.stats = {
            "executions": 0, "successes": 0, "failures": 0,
            "total_cost": 0.0, "avg_self_score": 0.0,
            "avg_ethical_score": 0.0, "avg_safety_score": 0.0
        }
        
        print(f"🤖 Hyper Agent [{profile.agent_name}] v{profile.version} inicializado")
    
    @property
    def cortex(self) -> HyperCortex:
        if self._cortex is None:
            self._cortex = HyperCortex(self.profile.agent_id, self.profile.tenant_id)
        return self._cortex
    
    @property
    def memory(self):
        if self._memory is None:
            from ..memory.quantum_memory import QuantumMemory
            self._memory = QuantumMemory(self.profile.tenant_id, self.profile.agent_id)
        return self._memory
    
    @property
    def rl_engine(self):
        if self._rl_engine is None:
            from ..learning.rl_engine import RLLearningEngine
            self._rl_engine = RLLearningEngine(self.profile.agent_id, self.profile.tenant_id)
        return self._rl_engine
    
    @property
    def budget_manager(self):
        if self._budget_manager is None:
            from ..budget.budget_manager import BudgetManager
            self._budget_manager = BudgetManager(self.profile.tenant_id)
        return self._budget_manager
    
    @property
    def safety_filter(self):
        if self._safety_filter is None:
            from ..safety.safety_filter import SafetyFilter
            self._safety_filter = SafetyFilter(self.profile.tenant_id)
        return self._safety_filter
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        pass
    
    @abstractmethod
    async def execute_task(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Tuple[str, List[ActionDef]]:
        pass
    
    async def run(self, input_data: Dict[str, Any]) -> HyperAgentOutput:
        """Punto de entrada principal - Ciclo completo nivel 0.1%"""
        start_time = datetime.utcnow()
        output = HyperAgentOutput(success=False, agent_id=self.profile.agent_id, tenant_id=self.profile.tenant_id)
        
        try:
            # PASO 1: Verificar presupuesto
            budget_status = self.budget_manager.get_budget_status()
            output.budget_status = budget_status
            model = self.budget_manager.select_model(self.profile.default_model, 0.7, 1000)
            
            # PASO 2: Recuperar contexto
            query = json.dumps(input_data, ensure_ascii=False)[:500]
            memory_context = await self.memory.get_context(query, limit=5)
            
            # PASO 3: Pensar en paralelo
            parallel_result = await self.cortex.parallel_think(query, {"memory": memory_context}, 3, self._generate)
            output.parallel_thoughts = {
                "consensus_level": parallel_result.get("consensus_level", 0),
                "recommended_action": parallel_result.get("recommended_action", ""),
                "streams_count": len(parallel_result.get("streams", []))
            }
            
            # PASO 4: Evaluar ética
            ethical_result = await self.cortex.ethical_assessment({"input": input_data})
            output.ethical_assessment = {
                "score": ethical_result.overall_score,
                "recommendation": ethical_result.recommendation,
                "concerns": ethical_result.concerns
            }
            
            if ethical_result.recommendation == "REJECT":
                output.error = "Rechazado por evaluación ética"
                return output
            
            # PASO 5: Ejecutar tarea
            execution_context = {
                "parallel_thoughts": parallel_result, "memory_context": memory_context,
                "ethical_assessment": ethical_result, "model": model
            }
            content, actions = await self.execute_task(input_data, execution_context)
            output.content = content
            output.actions = actions
            
            # PASO 6: Verificar seguridad
            if content:
                safety_result = self.safety_filter.check_content(content, "general", self.profile.agent_id)
                output.safety_check = {
                    "is_safe": safety_result.is_safe, "level": safety_result.safety_level.value,
                    "score": safety_result.score, "issues_count": len(safety_result.issues)
                }
                if safety_result.modified_content:
                    output.content = safety_result.modified_content
                if not safety_result.is_safe:
                    for action in output.actions:
                        action.requires_approval = True
            
            # PASO 7: Reflexionar
            reflection, self_score = await self._reflect(input_data, output)
            output.reflection = reflection
            output.self_score = self_score
            
            # PASO 8: Aprender
            action_key = output.actions[0].action.value if output.actions else "none"
            rl_update = self.rl_engine.update_policy("task_execution", action_key, True, self_score, output.cost_usd)
            output.learnings.append(f"RL: reward={rl_update.get('reward', 0):.3f}")
            
            # PASO 9: Guardar memoria
            await self.memory.store(
                f"exec_{datetime.utcnow().strftime('%H%M%S')}",
                {"input": str(input_data)[:200], "output": str(content)[:200], "score": self_score},
                MemoryType.SHORT_TERM, self_score, tags=[self.profile.category]
            )
            
            output.success = True
            
        except Exception as e:
            output.success = False
            output.error = str(e)
            self.rl_engine.update_policy("task_execution", "error", False, 0.0, output.cost_usd)
        
        output.execution_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        self._update_stats(output)
        return output
    
    async def _generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        model = kwargs.get("model", self.profile.default_model)
        result = await self.llm.generate(prompt=prompt, model=model, **kwargs)
        
        input_tokens = result.get("input_tokens", len(prompt) // 4)
        output_tokens = result.get("output_tokens", 100)
        self.budget_manager.record_usage(self.profile.agent_id, model, input_tokens, output_tokens)
        self.stats["total_cost"] += result.get("cost", 0)
        
        return result
    
    async def _reflect(self, input_data: Dict, output: HyperAgentOutput) -> Tuple[str, float]:
        prompt = f"""Evalúa el resultado:
TAREA: {json.dumps(input_data, ensure_ascii=False)[:200]}
CONTENIDO: {output.content[:150] if output.content else 'N/A'}

Responde:
SCORE: [0.0-1.0]
REFLEXIÓN: [evaluación breve]"""
        
        result = await self._generate(prompt, max_tokens=150)
        text = result.get("content", "")
        
        try:
            if "SCORE:" in text:
                numbers = re.findall(r'[\d.]+', text.split("SCORE:")[1].split("\n")[0])
                self_score = float(numbers[0]) if numbers else 0.75
            else:
                self_score = 0.75
        except:
            self_score = 0.75
        
        return text, max(0.0, min(1.0, self_score))
    
    def create_action(self, action_type: ActionType, params: Dict, **kwargs) -> ActionDef:
        confidence = kwargs.get("confidence", 0.9)
        best_actions = self.rl_engine.get_best_actions("task_execution", 3)
        for ba in best_actions:
            if ba["action"] == action_type.value:
                confidence = (confidence + ba["confidence"]) / 2
                break
        
        requires_approval = self.profile.autonomy_level in [AutonomyLevel.MANUAL, AutonomyLevel.LEARNING] or confidence < 0.7
        
        return ActionDef(
            action=action_type, params=params, confidence=confidence,
            priority=kwargs.get("priority", 5), requires_approval=requires_approval,
            agent_id=self.profile.agent_id, tenant_id=self.profile.tenant_id,
            reasoning=kwargs.get("reasoning", "")
        )
    
    def _update_stats(self, output: HyperAgentOutput):
        self.stats["executions"] += 1
        if output.success:
            self.stats["successes"] += 1
        else:
            self.stats["failures"] += 1
        
        n = self.stats["executions"]
        self.stats["avg_self_score"] = (self.stats["avg_self_score"] * (n-1) + output.self_score) / n
    
    def get_full_stats(self) -> Dict[str, Any]:
        return {
            "agent": {"id": self.profile.agent_id, "name": self.profile.agent_name, "version": self.profile.version},
            "performance": {
                "executions": self.stats["executions"],
                "success_rate": self.stats["successes"] / max(self.stats["executions"], 1),
                "avg_self_score": round(self.stats["avg_self_score"], 3),
                "total_cost": round(self.stats["total_cost"], 6)
            }
        }
