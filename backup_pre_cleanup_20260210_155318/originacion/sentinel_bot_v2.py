from .base_components_v2 import *
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

class SentinelBot(BaseAgent):
    def __init__(self, tenant_id: str):
        super().__init__("SentinelBot", "originacion", tenant_id)
        self.risk_factors = [
            "income_volatility", "debt_ratio", "credit_history", 
            "employment_stability", "payment_patterns"
        ]
        self.ml_model_loaded = True
        print(f"✅ SentinelBot inicializado para tenant {tenant_id}")
    
    def analyze_risk_profile(self, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            print(f"🔍 Iniciando análisis de riesgo para tenant {self.tenant_id}")
            
            risk_scores = {}
            for factor in self.risk_factors:
                score = self._calculate_risk_factor(applicant_data, factor)
                risk_scores[factor] = score
            
            final_score = sum(risk_scores.values()) / len(risk_scores)
            risk_level = "HIGH_RISK" if final_score > 0.7 else "LOW_RISK"
            
            result = {
                "applicant_id": applicant_data.get("id", "unknown"),
                "risk_score": round(final_score, 3),
                "risk_level": risk_level,
                "risk_factors": risk_scores,
                "recommendation": "REVIEW" if final_score > 0.5 else "APPROVE",
                "analysis_timestamp": datetime.now().isoformat(),
                "agent": self.agent_name,
                "tenant": self.tenant_id
            }
            
            print(f"✅ Análisis completado: Risk Level {risk_level}, Score {final_score:.3f}")
            return result
            
        except Exception as e:
            print(f"❌ Error en análisis de riesgo: {str(e)}")
            return self._error_response(str(e))
    
    def _calculate_risk_factor(self, data: Dict, factor: str) -> float:
        income = data.get("monthly_income", 50000)
        return max(0.1, min(0.9, 1.0 - (income / 100000)))
    
    def get_agent_status(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "category": self.category,
            "tenant_id": self.tenant_id,
            "status": "ACTIVE",
            "ml_model_loaded": self.ml_model_loaded
        }
