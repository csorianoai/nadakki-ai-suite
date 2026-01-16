"""
NADAKKI AI SUITE - RL LEARNING ENGINE
Motor de aprendizaje por refuerzo con UCB y Thompson Sampling.
Permite a los agentes mejorar continuamente basándose en resultados.
"""

import math
import random
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict


# ============================================================================
# ACTION STATS
# ============================================================================

@dataclass
class ActionStats:
    """Estadísticas de una acción para RL"""
    action: str
    total_attempts: int = 0
    successes: int = 0
    failures: int = 0
    total_reward: float = 0.0
    total_cost: float = 0.0
    avg_reward: float = 0.0
    confidence: float = 0.5
    last_used: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    # Para Thompson Sampling
    alpha: float = 1.0  # Beta distribution parameter (successes + 1)
    beta: float = 1.0   # Beta distribution parameter (failures + 1)
    
    def update(self, success: bool, reward: float, cost: float = 0.0):
        """Actualiza estadísticas después de una ejecución"""
        self.total_attempts += 1
        self.total_reward += reward
        self.total_cost += cost
        self.last_used = datetime.utcnow().isoformat()
        
        if success:
            self.successes += 1
            self.alpha += 1
        else:
            self.failures += 1
            self.beta += 1
        
        # Calcular promedio
        if self.total_attempts > 0:
            self.avg_reward = self.total_reward / self.total_attempts
            self.confidence = self.successes / self.total_attempts
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "total_attempts": self.total_attempts,
            "successes": self.successes,
            "failures": self.failures,
            "success_rate": self.confidence,
            "avg_reward": round(self.avg_reward, 4),
            "total_cost": round(self.total_cost, 6),
            "alpha": self.alpha,
            "beta": self.beta,
            "last_used": self.last_used
        }


# ============================================================================
# RL LEARNING ENGINE
# ============================================================================

class RLLearningEngine:
    """
    Motor de aprendizaje por refuerzo para agentes.
    
    Algoritmos soportados:
    - UCB (Upper Confidence Bound)
    - Thompson Sampling
    - Epsilon-Greedy
    - Softmax
    
    Características:
    - Multi-contexto (diferentes situaciones)
    - Decay temporal
    - Exploración vs explotación configurable
    """
    
    def __init__(
        self, 
        agent_id: str, 
        tenant_id: str = "default",
        exploration_rate: float = 0.1,
        algorithm: str = "ucb"
    ):
        self.agent_id = agent_id
        self.tenant_id = tenant_id
        self.exploration_rate = exploration_rate
        self.algorithm = algorithm
        
        # Estadísticas por contexto y acción
        # context -> action -> ActionStats
        self.action_stats: Dict[str, Dict[str, ActionStats]] = defaultdict(dict)
        
        # Historial de decisiones para análisis
        self.decision_history: List[Dict] = []
        
        # Configuración
        self.config = {
            "ucb_c": 2.0,  # Parámetro de exploración UCB
            "softmax_temperature": 1.0,
            "min_exploration": 0.01,
            "decay_rate": 0.995
        }
        
        # Estadísticas globales
        self.global_stats = {
            "total_decisions": 0,
            "explorations": 0,
            "exploitations": 0,
            "total_reward": 0.0
        }
    
    def update_policy(
        self,
        context: str,
        action: str,
        success: bool,
        reward: float,
        cost: float = 0.0
    ) -> Dict[str, Any]:
        """
        Actualiza la política basándose en el resultado de una acción.
        
        Args:
            context: Contexto de la decisión (ej: "content_generation")
            action: Acción tomada (ej: "social_post")
            success: Si la acción fue exitosa
            reward: Recompensa obtenida (0.0-1.0)
            cost: Costo de la acción en USD
        
        Returns:
            Dict con estadísticas actualizadas
        """
        # Crear stats si no existe
        if action not in self.action_stats[context]:
            self.action_stats[context][action] = ActionStats(action=action)
        
        # Actualizar
        stats = self.action_stats[context][action]
        stats.update(success, reward, cost)
        
        # Actualizar globales
        self.global_stats["total_reward"] += reward
        
        # Registrar en historial
        self.decision_history.append({
            "context": context,
            "action": action,
            "success": success,
            "reward": reward,
            "cost": cost,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Limitar historial
        if len(self.decision_history) > 1000:
            self.decision_history = self.decision_history[-500:]
        
        return {
            "action": action,
            "new_confidence": stats.confidence,
            "avg_reward": stats.avg_reward,
            "total_attempts": stats.total_attempts,
            "reward": reward
        }
    
    def select_action(
        self,
        context: str,
        available_actions: List[str],
        force_explore: bool = False
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Selecciona la mejor acción usando el algoritmo configurado.
        
        Args:
            context: Contexto de la decisión
            available_actions: Lista de acciones disponibles
            force_explore: Forzar exploración
        
        Returns:
            Tuple (acción seleccionada, metadatos de decisión)
        """
        if not available_actions:
            return "", {"error": "No actions available"}
        
        self.global_stats["total_decisions"] += 1
        
        # Verificar si explorar o explotar
        explore = force_explore or random.random() < self.exploration_rate
        
        if explore:
            self.global_stats["explorations"] += 1
            # Selección aleatoria
            selected = random.choice(available_actions)
            return selected, {
                "method": "exploration",
                "reason": "random_selection"
            }
        
        self.global_stats["exploitations"] += 1
        
        # Seleccionar según algoritmo
        if self.algorithm == "ucb":
            return self._select_ucb(context, available_actions)
        elif self.algorithm == "thompson":
            return self._select_thompson(context, available_actions)
        elif self.algorithm == "softmax":
            return self._select_softmax(context, available_actions)
        else:
            return self._select_greedy(context, available_actions)
    
    def _select_ucb(
        self, 
        context: str, 
        actions: List[str]
    ) -> Tuple[str, Dict[str, Any]]:
        """Upper Confidence Bound selection"""
        total_attempts = sum(
            self.action_stats[context].get(a, ActionStats(a)).total_attempts
            for a in actions
        )
        
        if total_attempts == 0:
            # Si no hay datos, seleccionar aleatorio
            return random.choice(actions), {"method": "ucb", "reason": "no_data"}
        
        best_action = None
        best_ucb = float('-inf')
        ucb_scores = {}
        
        for action in actions:
            stats = self.action_stats[context].get(action, ActionStats(action))
            
            if stats.total_attempts == 0:
                # Priorizar acciones no probadas
                ucb = float('inf')
            else:
                # UCB = avg_reward + c * sqrt(ln(N) / n)
                exploitation = stats.avg_reward
                exploration = self.config["ucb_c"] * math.sqrt(
                    math.log(total_attempts + 1) / stats.total_attempts
                )
                ucb = exploitation + exploration
            
            ucb_scores[action] = ucb
            
            if ucb > best_ucb:
                best_ucb = ucb
                best_action = action
        
        return best_action, {
            "method": "ucb",
            "ucb_scores": {k: round(v, 4) for k, v in ucb_scores.items()},
            "selected_ucb": round(best_ucb, 4)
        }
    
    def _select_thompson(
        self, 
        context: str, 
        actions: List[str]
    ) -> Tuple[str, Dict[str, Any]]:
        """Thompson Sampling selection"""
        samples = {}
        
        for action in actions:
            stats = self.action_stats[context].get(action, ActionStats(action))
            # Sample from Beta distribution
            sample = random.betavariate(stats.alpha, stats.beta)
            samples[action] = sample
        
        # Seleccionar acción con mayor sample
        best_action = max(samples.keys(), key=lambda a: samples[a])
        
        return best_action, {
            "method": "thompson_sampling",
            "samples": {k: round(v, 4) for k, v in samples.items()},
            "selected_sample": round(samples[best_action], 4)
        }
    
    def _select_softmax(
        self, 
        context: str, 
        actions: List[str]
    ) -> Tuple[str, Dict[str, Any]]:
        """Softmax (Boltzmann) selection"""
        temperature = self.config["softmax_temperature"]
        
        # Calcular exponenciales
        exp_values = {}
        for action in actions:
            stats = self.action_stats[context].get(action, ActionStats(action))
            exp_values[action] = math.exp(stats.avg_reward / temperature)
        
        # Normalizar probabilidades
        total = sum(exp_values.values())
        probs = {a: v / total for a, v in exp_values.items()}
        
        # Seleccionar según probabilidades
        r = random.random()
        cumulative = 0.0
        
        for action, prob in probs.items():
            cumulative += prob
            if r <= cumulative:
                return action, {
                    "method": "softmax",
                    "probabilities": {k: round(v, 4) for k, v in probs.items()},
                    "selected_prob": round(prob, 4)
                }
        
        # Fallback
        return actions[-1], {"method": "softmax", "reason": "fallback"}
    
    def _select_greedy(
        self, 
        context: str, 
        actions: List[str]
    ) -> Tuple[str, Dict[str, Any]]:
        """Greedy selection (siempre mejor acción conocida)"""
        best_action = None
        best_reward = float('-inf')
        
        for action in actions:
            stats = self.action_stats[context].get(action, ActionStats(action))
            if stats.avg_reward > best_reward:
                best_reward = stats.avg_reward
                best_action = action
        
        if best_action is None:
            best_action = random.choice(actions)
        
        return best_action, {
            "method": "greedy",
            "selected_reward": round(best_reward, 4)
        }
    
    def get_best_actions(
        self, 
        context: str, 
        top_n: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Retorna las mejores acciones para un contexto.
        
        Args:
            context: Contexto a consultar
            top_n: Número de mejores acciones a retornar
        
        Returns:
            Lista de acciones con estadísticas
        """
        if context not in self.action_stats:
            return []
        
        actions = []
        for action, stats in self.action_stats[context].items():
            actions.append({
                "action": action,
                "confidence": round(stats.confidence, 3),
                "avg_reward": round(stats.avg_reward, 3),
                "attempts": stats.total_attempts,
                "success_rate": round(stats.successes / max(stats.total_attempts, 1), 3)
            })
        
        # Ordenar por reward promedio
        actions.sort(key=lambda x: x["avg_reward"], reverse=True)
        
        return actions[:top_n]
    
    def decay_exploration(self):
        """Reduce la tasa de exploración gradualmente"""
        self.exploration_rate = max(
            self.config["min_exploration"],
            self.exploration_rate * self.config["decay_rate"]
        )
        return self.exploration_rate
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Retorna resumen del aprendizaje"""
        contexts_summary = {}
        
        for context, actions in self.action_stats.items():
            best_action = max(
                actions.values(),
                key=lambda s: s.avg_reward,
                default=ActionStats("")
            )
            
            contexts_summary[context] = {
                "num_actions": len(actions),
                "best_action": best_action.action,
                "best_reward": round(best_action.avg_reward, 4),
                "total_attempts": sum(s.total_attempts for s in actions.values())
            }
        
        return {
            "agent_id": self.agent_id,
            "tenant_id": self.tenant_id,
            "algorithm": self.algorithm,
            "exploration_rate": round(self.exploration_rate, 4),
            "global_stats": self.global_stats,
            "contexts": contexts_summary,
            "recent_decisions": len(self.decision_history)
        }
    
    def export_policy(self) -> Dict[str, Any]:
        """Exporta política aprendida para persistencia"""
        return {
            "agent_id": self.agent_id,
            "tenant_id": self.tenant_id,
            "algorithm": self.algorithm,
            "exploration_rate": self.exploration_rate,
            "config": self.config,
            "global_stats": self.global_stats,
            "action_stats": {
                context: {
                    action: stats.to_dict()
                    for action, stats in actions.items()
                }
                for context, actions in self.action_stats.items()
            },
            "exported_at": datetime.utcnow().isoformat()
        }
    
    def import_policy(self, data: Dict[str, Any]):
        """Importa política desde export"""
        self.exploration_rate = data.get("exploration_rate", 0.1)
        self.config.update(data.get("config", {}))
        self.global_stats.update(data.get("global_stats", {}))
        
        for context, actions in data.get("action_stats", {}).items():
            for action, stats_dict in actions.items():
                stats = ActionStats(action=action)
                stats.total_attempts = stats_dict.get("total_attempts", 0)
                stats.successes = stats_dict.get("successes", 0)
                stats.failures = stats_dict.get("failures", 0)
                stats.avg_reward = stats_dict.get("avg_reward", 0.0)
                stats.total_cost = stats_dict.get("total_cost", 0.0)
                stats.alpha = stats_dict.get("alpha", 1.0)
                stats.beta = stats_dict.get("beta", 1.0)
                stats.confidence = stats_dict.get("success_rate", 0.5)
                
                self.action_stats[context][action] = stats
