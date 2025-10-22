# ================================================================
# RISK ASSESSOR
# Evaluacion de riesgo multivariable
# ================================================================

import json
import time
from datetime import datetime
from typing import Dict, List, Any

class RiskAssessor:
    def __init__(self, tenant_id: str = None):
        self.tenant_id = tenant_id
        self.agent_name = "RiskAssessor"
        self.version = "1.0.0"
        
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        
        client_data = data.get("client_data", {})
        financial_data = data.get("financial_data", {})
        credit_history = data.get("credit_history", {})
        
        risk_score = 0.0
        risk_factors = []
        
        # Analisis de edad
        age = client_data.get("age", 25)
        if 25 <= age <= 65:
            risk_score += 0.1
        else:
            risk_factors.append("Edad fuera del rango optimo")
            
        # Analisis de ingresos
        monthly_income = financial_data.get("monthly_income", 0)
        if monthly_income >= 50000:
            risk_score += 0.3
        elif monthly_income >= 25000:
            risk_score += 0.2
        else:
            risk_factors.append("Ingresos insuficientes")
            
        # Historial crediticio
        credit_score = credit_history.get("score", 0)
        if credit_score >= 700:
            risk_score += 0.4
        elif credit_score >= 600:
            risk_score += 0.25
        else:
            risk_factors.append("Historial crediticio deficiente")
            
        # Estabilidad laboral
        job_tenure = client_data.get("job_tenure_months", 0)
        if job_tenure >= 24:
            risk_score += 0.2
        elif job_tenure >= 12:
            risk_score += 0.1
        else:
            risk_factors.append("Baja estabilidad laboral")
            
        if risk_score >= 0.8:
            risk_level = "low"
        elif risk_score >= 0.6:
            risk_level = "medium"
        else:
            risk_level = "high"
            
        return {
            "success": True,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "recommendation": "approve" if risk_score >= 0.6 else "reject",
            "processing_time": time.time() - start_time,
            "timestamp": datetime.now().isoformat()
        }
        
    def health_check(self):
        return {"agent": self.agent_name, "status": "healthy"}
