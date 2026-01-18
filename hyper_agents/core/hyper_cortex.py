"""
NADAKKI AI SUITE - HYPER CORTEX
Sistema de pensamiento paralelo y evaluación ética.
Nivel 0.1% - Múltiples streams de pensamiento.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field

from .types import EthicalAssessment


# ============================================================================
# HYPER CORTEX - PENSAMIENTO PARALELO
# ============================================================================

class HyperCortex:
    """
    Sistema de pensamiento paralelo nivel 0.1%
    
    Capacidades:
    - Múltiples streams de pensamiento simultáneos
    - Evaluación ética integrada
    - Síntesis de consenso
    - Meta-cognición
    """
    
    def __init__(self, agent_id: str, tenant_id: str = "default"):
        self.agent_id = agent_id
        self.tenant_id = tenant_id
        self.thought_history: List[Dict] = []
        self.ethical_cache: Dict[str, EthicalAssessment] = {}
    
    async def parallel_think(
        self,
        query: str,
        context: Dict[str, Any],
        num_streams: int = 3,
        generate_fn: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta pensamiento paralelo en múltiples streams.
        
        Args:
            query: Pregunta o tarea a procesar
            context: Contexto adicional (memoria, datos previos)
            num_streams: Número de streams paralelos (2-7)
            generate_fn: Función de generación LLM (async)
        
        Returns:
            Dict con streams, consenso y recomendación
        """
        num_streams = max(2, min(7, num_streams))
        
        # Crear prompts diferenciados para cada stream
        stream_prompts = self._create_stream_prompts(query, context, num_streams)
        
        # Si no hay función de generación, usar respuestas simuladas
        if generate_fn is None:
            streams = [
                {
                    "stream_id": i,
                    "perspective": stream_prompts[i]["perspective"],
                    "analysis": f"Análisis desde perspectiva {stream_prompts[i]['perspective']}: {query[:50]}...",
                    "confidence": 0.7 + (i * 0.05),
                    "key_points": [f"Punto clave {j+1}" for j in range(3)],
                    "recommendation": "proceed" if i % 2 == 0 else "review"
                }
                for i in range(num_streams)
            ]
        else:
            # Ejecutar streams en paralelo
            tasks = [
                self._execute_stream(i, stream_prompts[i], generate_fn)
                for i in range(num_streams)
            ]
            streams = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filtrar errores
            streams = [
                s for s in streams 
                if isinstance(s, dict) and "error" not in s
            ]
        
        # Calcular consenso
        consensus = self._calculate_consensus(streams)
        
        # Determinar acción recomendada
        recommended_action = self._determine_action(consensus, streams)
        
        result = {
            "streams": streams,
            "num_streams": len(streams),
            "consensus_level": consensus["level"],
            "consensus_details": consensus,
            "recommended_action": recommended_action,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Guardar en historial
        self.thought_history.append({
            "query": query[:200],
            "result": result,
            "timestamp": result["timestamp"]
        })
        
        return result
    
    def _create_stream_prompts(
        self, 
        query: str, 
        context: Dict, 
        num_streams: int
    ) -> List[Dict]:
        """Crea prompts diferenciados para cada stream"""
        perspectives = [
            {"perspective": "analytical", "focus": "datos y métricas", "style": "objetivo y cuantitativo"},
            {"perspective": "creative", "focus": "innovación y alternativas", "style": "divergente y exploratorio"},
            {"perspective": "critical", "focus": "riesgos y objeciones", "style": "escéptico y cauteloso"},
            {"perspective": "practical", "focus": "implementación y viabilidad", "style": "pragmático"},
            {"perspective": "strategic", "focus": "impacto a largo plazo", "style": "visionario"},
            {"perspective": "empathetic", "focus": "impacto en usuarios", "style": "centrado en personas"},
            {"perspective": "systemic", "focus": "interconexiones y efectos", "style": "holístico"}
        ]
        
        prompts = []
        for i in range(num_streams):
            p = perspectives[i % len(perspectives)]
            prompts.append({
                "stream_id": i,
                "perspective": p["perspective"],
                "prompt": f"""Analiza desde perspectiva {p['perspective'].upper()}:
TAREA: {query}

CONTEXTO: {json.dumps(context, ensure_ascii=False)[:300]}

ENFOQUE: {p['focus']}
ESTILO: {p['style']}

Responde en formato:
ANÁLISIS: [tu análisis desde esta perspectiva]
PUNTOS_CLAVE: [lista de 3 puntos]
CONFIANZA: [0.0-1.0]
RECOMENDACIÓN: [proceed/review/reject]"""
            })
        
        return prompts
    
    async def _execute_stream(
        self, 
        stream_id: int, 
        prompt_config: Dict, 
        generate_fn: Callable
    ) -> Dict[str, Any]:
        """Ejecuta un stream de pensamiento"""
        try:
            result = await generate_fn(prompt_config["prompt"], max_tokens=500)
            content = result.get("content", "")
            
            # Parsear respuesta
            analysis = ""
            key_points = []
            confidence = 0.75
            recommendation = "proceed"
            
            if "ANÁLISIS:" in content:
                parts = content.split("ANÁLISIS:")
                if len(parts) > 1:
                    analysis = parts[1].split("PUNTOS_CLAVE:")[0].strip()
            
            if "CONFIANZA:" in content:
                try:
                    conf_str = content.split("CONFIANZA:")[1].split("\n")[0].strip()
                    confidence = float(conf_str.replace("[", "").replace("]", ""))
                except:
                    pass
            
            if "RECOMENDACIÓN:" in content:
                rec = content.split("RECOMENDACIÓN:")[1].split("\n")[0].strip().lower()
                if "reject" in rec:
                    recommendation = "reject"
                elif "review" in rec:
                    recommendation = "review"
            
            return {
                "stream_id": stream_id,
                "perspective": prompt_config["perspective"],
                "analysis": analysis or content[:200],
                "confidence": confidence,
                "key_points": key_points or ["Análisis completado"],
                "recommendation": recommendation
            }
            
        except Exception as e:
            return {
                "stream_id": stream_id,
                "perspective": prompt_config["perspective"],
                "error": str(e),
                "confidence": 0.0,
                "recommendation": "review"
            }
    
    def _calculate_consensus(self, streams: List[Dict]) -> Dict[str, Any]:
        """Calcula nivel de consenso entre streams"""
        if not streams:
            return {"level": 0.0, "agreement": "none", "details": {}}
        
        # Extraer confianzas y recomendaciones
        confidences = [s.get("confidence", 0.5) for s in streams]
        recommendations = [s.get("recommendation", "review") for s in streams]
        
        # Calcular consenso basado en similitud de recomendaciones
        rec_counts = {}
        for r in recommendations:
            rec_counts[r] = rec_counts.get(r, 0) + 1
        
        max_agreement = max(rec_counts.values()) / len(streams)
        avg_confidence = sum(confidences) / len(confidences)
        
        # Nivel de consenso combinado
        consensus_level = (max_agreement * 0.6) + (avg_confidence * 0.4)
        
        # Determinar tipo de acuerdo
        if consensus_level >= 0.8:
            agreement = "strong"
        elif consensus_level >= 0.6:
            agreement = "moderate"
        elif consensus_level >= 0.4:
            agreement = "weak"
        else:
            agreement = "none"
        
        return {
            "level": round(consensus_level, 3),
            "agreement": agreement,
            "avg_confidence": round(avg_confidence, 3),
            "recommendation_distribution": rec_counts,
            "dominant_recommendation": max(rec_counts.keys(), key=lambda k: rec_counts[k])
        }
    
    def _determine_action(self, consensus: Dict, streams: List[Dict]) -> str:
        """Determina acción recomendada basada en consenso"""
        level = consensus.get("level", 0)
        dominant = consensus.get("dominant_recommendation", "review")
        
        if level >= 0.8 and dominant == "proceed":
            return "EXECUTE_NOW"
        elif level >= 0.6 and dominant != "reject":
            return "PROCEED_WITH_CAUTION"
        elif dominant == "reject" or level < 0.4:
            return "REQUIRES_REVIEW"
        else:
            return "NEEDS_MORE_DATA"
    
    async def ethical_assessment(
        self, 
        action_context: Dict[str, Any],
        generate_fn: Optional[Callable] = None
    ) -> EthicalAssessment:
        """
        Evalúa las implicaciones éticas de una acción.
        
        Args:
            action_context: Contexto de la acción a evaluar
            generate_fn: Función de generación LLM (opcional)
        
        Returns:
            EthicalAssessment con score, recomendación y concerns
        """
        # Crear hash del contexto para cache
        context_key = json.dumps(action_context, sort_keys=True)[:100]
        
        if context_key in self.ethical_cache:
            return self.ethical_cache[context_key]
        
        # Criterios de evaluación ética
        criteria = {
            "fairness": self._evaluate_fairness(action_context),
            "transparency": self._evaluate_transparency(action_context),
            "privacy": self._evaluate_privacy(action_context),
            "harm_prevention": self._evaluate_harm_prevention(action_context),
            "accountability": self._evaluate_accountability(action_context)
        }
        
        # Calcular score general
        weights = {
            "fairness": 0.25,
            "transparency": 0.20,
            "privacy": 0.25,
            "harm_prevention": 0.20,
            "accountability": 0.10
        }
        
        overall_score = sum(
            criteria[k]["score"] * weights[k] 
            for k in criteria.keys()
        )
        
        # Recopilar concerns
        concerns = []
        for criterion, result in criteria.items():
            if result["score"] < 0.7:
                concerns.append(f"{criterion}: {result['concern']}")
        
        # Determinar recomendación
        if overall_score >= 0.8 and not concerns:
            recommendation = "APPROVE"
        elif overall_score >= 0.6:
            recommendation = "REVIEW"
        else:
            recommendation = "REJECT"
        
        assessment = EthicalAssessment(
            overall_score=round(overall_score, 3),
            recommendation=recommendation,
            concerns=concerns,
            details={
                "criteria_scores": {k: v["score"] for k, v in criteria.items()},
                "weights": weights,
                "evaluated_at": datetime.utcnow().isoformat()
            }
        )
        
        # Guardar en cache
        self.ethical_cache[context_key] = assessment
        
        return assessment
    
    def _evaluate_fairness(self, context: Dict) -> Dict:
        """Evalúa justicia y equidad"""
        # Verificar si hay sesgo potencial
        input_data = str(context.get("input", "")).lower()
        
        bias_indicators = ["solo para", "exclusivo", "discriminar", "excluir"]
        has_bias = any(ind in input_data for ind in bias_indicators)
        
        score = 0.6 if has_bias else 0.9
        return {
            "score": score,
            "concern": "Posible sesgo detectado en los criterios" if has_bias else None
        }
    
    def _evaluate_transparency(self, context: Dict) -> Dict:
        """Evalúa transparencia de la acción"""
        # Verificar si hay información oculta
        has_reasoning = "reasoning" in context or "explanation" in context
        score = 0.9 if has_reasoning else 0.7
        return {
            "score": score,
            "concern": "Falta explicación del razonamiento" if not has_reasoning else None
        }
    
    def _evaluate_privacy(self, context: Dict) -> Dict:
        """Evalúa protección de privacidad"""
        input_str = str(context).lower()
        
        # Detectar datos sensibles
        sensitive_terms = ["ssn", "password", "credit card", "tarjeta", "cedula", "social security"]
        has_sensitive = any(term in input_str for term in sensitive_terms)
        
        score = 0.5 if has_sensitive else 0.95
        return {
            "score": score,
            "concern": "Datos sensibles detectados - requiere protección adicional" if has_sensitive else None
        }
    
    def _evaluate_harm_prevention(self, context: Dict) -> Dict:
        """Evalúa prevención de daños"""
        input_str = str(context).lower()
        
        # Detectar contenido potencialmente dañino
        harmful_terms = ["hackear", "robar", "fraude", "ilegal", "violencia"]
        is_harmful = any(term in input_str for term in harmful_terms)
        
        score = 0.2 if is_harmful else 0.95
        return {
            "score": score,
            "concern": "Contenido potencialmente dañino detectado" if is_harmful else None
        }
    
    def _evaluate_accountability(self, context: Dict) -> Dict:
        """Evalúa trazabilidad y responsabilidad"""
        has_audit = "audit" in str(context).lower() or "log" in str(context).lower()
        has_agent_id = "agent_id" in context
        
        score = 0.95 if (has_audit or has_agent_id) else 0.7
        return {
            "score": score,
            "concern": "Falta identificación del agente responsable" if not has_agent_id else None
        }
    
    def get_thought_history(self, limit: int = 10) -> List[Dict]:
        """Retorna historial de pensamientos recientes"""
        return self.thought_history[-limit:]
    
    def clear_cache(self):
        """Limpia caches"""
        self.ethical_cache.clear()
        self.thought_history.clear()
