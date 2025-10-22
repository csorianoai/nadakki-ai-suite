from .base_components_v2 import *
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

class BehaviorMiner(BaseAgent):
    def __init__(self, tenant_id: str):
        super().__init__("BehaviorMiner", "originacion", tenant_id)
        self.behavioral_patterns = [
            "spending_velocity", "payment_timing", "transaction_diversity",
            "balance_stability", "channel_usage", "seasonal_patterns"
        ]
        self.risk_indicators = {}
        print(f"📈 BehaviorMiner inicializado para tenant {tenant_id}")
    
    def analyze_behavioral_patterns(self, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            print(f"📈 Analizando patrones de comportamiento para tenant {self.tenant_id}")
            
            # Análisis de patrones por categoría
            pattern_scores = {}
            for pattern in self.behavioral_patterns:
                score = self._analyze_pattern(applicant_data, pattern)
                pattern_scores[pattern] = score
            
            # Detección de comportamientos de riesgo
            risk_behaviors = self._detect_risk_behaviors(applicant_data, pattern_scores)
            
            # Score de estabilidad financiera
            stability_score = self._calculate_stability_score(pattern_scores)
            
            # Predicción de comportamiento futuro
            future_behavior = self._predict_future_behavior(pattern_scores, applicant_data)
            
            # Recomendaciones personalizadas
            recommendations = self._generate_recommendations(pattern_scores, risk_behaviors)
            
            result = {
                "applicant_id": applicant_data.get("id", "unknown"),
                "behavioral_patterns": pattern_scores,
                "stability_score": stability_score,
                "risk_behaviors": risk_behaviors,
                "future_behavior_prediction": future_behavior,
                "recommendations": recommendations,
                "behavioral_risk_level": self._classify_behavioral_risk(stability_score),
                "confidence_score": self._calculate_confidence(pattern_scores),
                "analysis_timestamp": datetime.now().isoformat(),
                "agent": self.agent_name,
                "tenant": self.tenant_id
            }
            
            print(f"✅ Análisis behavioral completado: Stability {stability_score:.3f}")
            return result
            
        except Exception as e:
            print(f"❌ Error en análisis behavioral: {str(e)}")
            return self._error_response(str(e))
    
    def _analyze_pattern(self, data: Dict, pattern: str) -> Dict[str, Any]:
        if pattern == "spending_velocity":
            monthly_income = data.get("monthly_income", 50000)
            avg_spending = data.get("avg_monthly_spending", monthly_income * 0.8)
            velocity = avg_spending / monthly_income if monthly_income > 0 else 1.0
            return {
                "score": round(min(1.0, velocity), 3),
                "risk_level": "HIGH" if velocity > 0.95 else "LOW",
                "details": f"Spending velocity: {velocity:.2f}"
            }
        
        elif pattern == "payment_timing":
            on_time_payments = data.get("on_time_payment_ratio", 0.85)
            avg_delay_days = data.get("avg_payment_delay_days", 2)
            timing_score = on_time_payments * (1 - min(avg_delay_days / 30, 1))
            return {
                "score": round(timing_score, 3),
                "risk_level": "LOW" if timing_score > 0.8 else "HIGH",
                "details": f"On-time ratio: {on_time_payments}, Avg delay: {avg_delay_days} days"
            }
        
        elif pattern == "transaction_diversity":
            transaction_types = data.get("transaction_types_count", 5)
            diversity_score = min(transaction_types / 10, 1.0)
            return {
                "score": round(diversity_score, 3),
                "risk_level": "LOW" if diversity_score > 0.5 else "MEDIUM",
                "details": f"Transaction types: {transaction_types}"
            }
        
        elif pattern == "balance_stability":
            min_balance = data.get("min_monthly_balance", 10000)
            avg_balance = data.get("avg_monthly_balance", 25000)
            stability = min_balance / avg_balance if avg_balance > 0 else 0
            return {
                "score": round(stability, 3),
                "risk_level": "LOW" if stability > 0.3 else "HIGH",
                "details": f"Balance stability ratio: {stability:.2f}"
            }
        
        elif pattern == "channel_usage":
            digital_ratio = data.get("digital_channel_usage", 0.7)
            return {
                "score": round(digital_ratio, 3),
                "risk_level": "LOW" if digital_ratio > 0.5 else "MEDIUM",
                "details": f"Digital channel usage: {digital_ratio:.2f}"
            }
        
        elif pattern == "seasonal_patterns":
            # Simulación de análisis estacional
            seasonal_variance = data.get("seasonal_spending_variance", 0.2)
            stability = 1 - seasonal_variance
            return {
                "score": round(stability, 3),
                "risk_level": "LOW" if stability > 0.7 else "MEDIUM",
                "details": f"Seasonal variance: {seasonal_variance:.2f}"
            }
        
        else:
            return {
                "score": 0.5,
                "risk_level": "MEDIUM",
                "details": "Pattern not analyzed"
            }
    
    def _detect_risk_behaviors(self, data: Dict, patterns: Dict) -> List[str]:
        risk_behaviors = []
        
        # Comportamientos de alto riesgo
        if patterns.get("spending_velocity", {}).get("score", 0) > 0.95:
            risk_behaviors.append("Excessive spending velocity detected")
        
        if patterns.get("payment_timing", {}).get("score", 0) < 0.6:
            risk_behaviors.append("Poor payment timing pattern")
        
        if patterns.get("balance_stability", {}).get("score", 0) < 0.2:
            risk_behaviors.append("Unstable account balance pattern")
        
        # Comportamientos específicos
        monthly_income = data.get("monthly_income", 0)
        if monthly_income > 0:
            credit_utilization = data.get("credit_utilization", 0)
            if credit_utilization > 0.8:
                risk_behaviors.append("High credit utilization ratio")
        
        return risk_behaviors
    
    def _calculate_stability_score(self, patterns: Dict) -> float:
        scores = [pattern.get("score", 0.5) for pattern in patterns.values()]
        if not scores:
            return 0.5
        
        # Promedio ponderado
        weights = [0.25, 0.20, 0.15, 0.20, 0.10, 0.10]  # Pesos por patrón
        weighted_score = sum(score * weight for score, weight in zip(scores, weights[:len(scores)]))
        return round(weighted_score, 3)
    
    def _predict_future_behavior(self, patterns: Dict, data: Dict) -> Dict[str, Any]:
        stability = self._calculate_stability_score(patterns)
        
        # Predicción basada en estabilidad actual
        if stability > 0.8:
            prediction = "STABLE"
            confidence = 0.9
        elif stability > 0.6:
            prediction = "MODERATELY_STABLE"
            confidence = 0.7
        else:
            prediction = "UNSTABLE"
            confidence = 0.8
        
        return {
            "prediction": prediction,
            "confidence": confidence,
            "projected_risk_trend": "DECREASING" if stability > 0.75 else "INCREASING",
            "recommendation_priority": "LOW" if stability > 0.8 else "HIGH"
        }
    
    def _generate_recommendations(self, patterns: Dict, risk_behaviors: List[str]) -> List[str]:
        recommendations = []
        
        if len(risk_behaviors) > 2:
            recommendations.append("Require additional financial counseling")
        
        payment_score = patterns.get("payment_timing", {}).get("score", 0.5)
        if payment_score < 0.7:
            recommendations.append("Set up automatic payment reminders")
        
        balance_score = patterns.get("balance_stability", {}).get("score", 0.5)
        if balance_score < 0.4:
            recommendations.append("Establish minimum balance requirements")
        
        if not recommendations:
            recommendations.append("Standard monitoring protocols apply")
        
        return recommendations
    
    def _classify_behavioral_risk(self, stability_score: float) -> str:
        if stability_score >= 0.8:
            return "LOW_BEHAVIORAL_RISK"
        elif stability_score >= 0.6:
            return "MEDIUM_BEHAVIORAL_RISK"
        else:
            return "HIGH_BEHAVIORAL_RISK"
    
    def _calculate_confidence(self, patterns: Dict) -> float:
        # Confianza basada en completitud de datos
        analyzed_patterns = sum(1 for pattern in patterns.values() if pattern.get("score", 0) > 0)
        confidence = analyzed_patterns / len(self.behavioral_patterns)
        return round(confidence, 3)
    
    def get_agent_status(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "category": self.category,
            "tenant_id": self.tenant_id,
            "status": "ACTIVE",
            "behavioral_patterns_count": len(self.behavioral_patterns),
            "risk_indicators_loaded": len(self.risk_indicators)
        }
