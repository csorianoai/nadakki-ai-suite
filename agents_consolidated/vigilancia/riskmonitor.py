# ================================================================
# RISK MONITOR
# Monitor de riesgo en tiempo real
# ================================================================

import json
import time
from datetime import datetime
from typing import Dict, List, Any

class RiskMonitor:
    def __init__(self, tenant_id: str = None):
        self.tenant_id = tenant_id
        self.agent_name = "RiskMonitor"
        self.version = "1.0.0"
        
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        
        portfolio_data = data.get("portfolio_data", {})
        client_id = data.get("client_id", "")
        current_metrics = data.get("current_metrics", {})
        
        alerts = []
        risk_level = "normal"
        monitoring_score = 1.0
        
        # Verificar ratio deuda/ingreso
        current_ratio = current_metrics.get("debt_to_income", 0)
        if current_ratio > 0.8:
            alerts.append("Ratio deuda/ingreso critico")
            risk_level = "critical"
            monitoring_score = 0.2
        elif current_ratio > 0.6:
            alerts.append("Ratio deuda/ingreso elevado")
            risk_level = "high"
            monitoring_score = 0.5
            
        # Verificar pagos atrasados
        days_overdue = current_metrics.get("days_overdue", 0)
        if days_overdue > 90:
            alerts.append("Mora critica detectada")
            risk_level = "critical"
            monitoring_score = min(monitoring_score, 0.1)
        elif days_overdue > 30:
            alerts.append("Mora detectada")
            if risk_level == "normal":
                risk_level = "high"
            monitoring_score = min(monitoring_score, 0.4)
            
        # Verificar cambios en ingresos
        income_change = current_metrics.get("income_change_pct", 0)
        if income_change < -0.3:
            alerts.append("Reduccion significativa de ingresos")
            if risk_level == "normal":
                risk_level = "high"
            monitoring_score = min(monitoring_score, 0.6)
            
        return {
            "success": True,
            "risk_level": risk_level,
            "monitoring_score": monitoring_score,
            "alerts": alerts,
            "requires_action": len(alerts) > 0,
            "recommended_action": "immediate_contact" if risk_level == "critical" else "monitor",
            "processing_time": time.time() - start_time,
            "timestamp": datetime.now().isoformat()
        }
        
    def health_check(self):
        return {"agent": self.agent_name, "status": "healthy"}
