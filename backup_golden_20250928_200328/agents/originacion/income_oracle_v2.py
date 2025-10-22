from .base_components_v2 import *
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import re

class IncomeOracle(BaseAgent):
    def __init__(self, tenant_id: str):
        super().__init__("IncomeOracle", "originacion", tenant_id)
        self.verification_sources = [
            "tss_payroll", "bank_statements", "tax_records", 
            "employment_verification", "third_party_apis"
        ]
        self.consistency_threshold = 0.85
        print(f"💰 IncomeOracle inicializado para tenant {tenant_id}")
    
    def verify_income_profile(self, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            print(f"💰 Verificando perfil de ingresos para tenant {self.tenant_id}")
            
            # Verificación por múltiples fuentes
            verification_results = {}
            for source in self.verification_sources:
                result = self._verify_income_source(applicant_data, source)
                verification_results[source] = result
            
            # Análisis de consistencia
            consistency_score = self._calculate_consistency(verification_results)
            
            # Detección de anomalías
            anomalies = self._detect_income_anomalies(applicant_data, verification_results)
            
            # Score final de confiabilidad
            reliability_score = self._calculate_reliability_score(
                consistency_score, anomalies, verification_results
            )
            
            result = {
                "applicant_id": applicant_data.get("id", "unknown"),
                "declared_income": applicant_data.get("monthly_income", 0),
                "verified_income": self._get_verified_income(verification_results),
                "consistency_score": consistency_score,
                "reliability_score": reliability_score,
                "verification_sources": verification_results,
                "anomalies_detected": anomalies,
                "verification_status": self._get_verification_status(reliability_score),
                "confidence_level": self._get_confidence_level(consistency_score),
                "analysis_timestamp": datetime.now().isoformat(),
                "agent": self.agent_name,
                "tenant": self.tenant_id
            }
            
            print(f"✅ Verificación completada: Reliability {reliability_score:.3f}")
            return result
            
        except Exception as e:
            print(f"❌ Error en verificación de ingresos: {str(e)}")
            return self._error_response(str(e))
    
    def _verify_income_source(self, data: Dict, source: str) -> Dict[str, Any]:
        declared_income = data.get("monthly_income", 0)
        
        if source == "tss_payroll":
            # Simulación API TSS
            tss_income = declared_income * (0.95 + (hash(str(declared_income)) % 10) / 100)
            return {
                "verified_amount": round(tss_income, 2),
                "status": "verified" if abs(tss_income - declared_income) < declared_income * 0.1 else "discrepancy",
                "confidence": 0.95,
                "source_reliability": 0.98
            }
        elif source == "bank_statements":
            # Simulación análisis estados bancarios
            bank_income = declared_income * (0.92 + (hash(str(declared_income + 1)) % 12) / 100)
            return {
                "verified_amount": round(bank_income, 2),
                "status": "verified" if abs(bank_income - declared_income) < declared_income * 0.15 else "discrepancy",
                "confidence": 0.88,
                "source_reliability": 0.85
            }
        elif source == "employment_verification":
            # Simulación verificación empleador
            emp_income = declared_income * (0.98 + (hash(str(declared_income + 2)) % 6) / 100)
            return {
                "verified_amount": round(emp_income, 2),
                "status": "verified" if abs(emp_income - declared_income) < declared_income * 0.05 else "discrepancy",
                "confidence": 0.92,
                "source_reliability": 0.90
            }
        else:
            # Fuentes secundarias
            return {
                "verified_amount": declared_income * 0.9,
                "status": "partial",
                "confidence": 0.70,
                "source_reliability": 0.75
            }
    
    def _calculate_consistency(self, verification_results: Dict) -> float:
        amounts = [result["verified_amount"] for result in verification_results.values()]
        if len(amounts) < 2:
            return 0.5
        
        avg_amount = sum(amounts) / len(amounts)
        variances = [(amount - avg_amount) ** 2 for amount in amounts]
        variance = sum(variances) / len(variances)
        consistency = max(0.0, 1.0 - (variance ** 0.5) / avg_amount) if avg_amount > 0 else 0.0
        
        return round(consistency, 3)
    
    def _detect_income_anomalies(self, data: Dict, verification_results: Dict) -> List[str]:
        anomalies = []
        declared = data.get("monthly_income", 0)
        
        # Verificar discrepancias grandes
        for source, result in verification_results.items():
            verified = result["verified_amount"]
            if abs(verified - declared) > declared * 0.2:
                anomalies.append(f"Large discrepancy in {source}: {verified} vs {declared}")
        
        # Verificar patrones sospechosos
        if declared % 1000 == 0 and declared > 50000:
            anomalies.append("Round number income pattern (potential inflation)")
        
        return anomalies
    
    def _calculate_reliability_score(self, consistency: float, anomalies: List, 
                                   verification_results: Dict) -> float:
        base_score = consistency
        
        # Penalizar por anomalías
        anomaly_penalty = len(anomalies) * 0.1
        base_score -= anomaly_penalty
        
        # Bonificar por fuentes confiables
        reliable_sources = sum(1 for result in verification_results.values() 
                             if result["source_reliability"] > 0.85)
        reliability_bonus = reliable_sources * 0.05
        base_score += reliability_bonus
        
        return round(max(0.0, min(1.0, base_score)), 3)
    
    def _get_verified_income(self, verification_results: Dict) -> float:
        # Promedio ponderado por confiabilidad
        total_weight = 0
        weighted_sum = 0
        
        for result in verification_results.values():
            weight = result["confidence"] * result["source_reliability"]
            weighted_sum += result["verified_amount"] * weight
            total_weight += weight
        
        return round(weighted_sum / total_weight if total_weight > 0 else 0, 2)
    
    def _get_verification_status(self, reliability_score: float) -> str:
        if reliability_score >= 0.85:
            return "VERIFIED"
        elif reliability_score >= 0.65:
            return "PARTIALLY_VERIFIED"
        else:
            return "UNVERIFIED"
    
    def _get_confidence_level(self, consistency_score: float) -> str:
        if consistency_score >= 0.9:
            return "HIGH"
        elif consistency_score >= 0.7:
            return "MEDIUM"
        else:
            return "LOW"
    
    def get_agent_status(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "category": self.category,
            "tenant_id": self.tenant_id,
            "status": "ACTIVE",
            "verification_sources_count": len(self.verification_sources),
            "consistency_threshold": self.consistency_threshold
        }
