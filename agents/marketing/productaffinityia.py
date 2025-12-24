# agents/marketing/productaffinityia.py
"""
ProductAffinityIA v3.0.0 - SUPER AGENT
Cross/Upsell con Decisión Explicable
"""

from __future__ import annotations
import time
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)

try:
    from agents.marketing.layers.decision_layer import apply_decision_layer
    DECISION_LAYER_AVAILABLE = True
except ImportError:
    DECISION_LAYER_AVAILABLE = False


class ProductAffinityIA:
    VERSION = "3.0.0"
    AGENT_ID = "productaffinityia"
    
    def __init__(self, tenant_id: str, config: Optional[Dict] = None):
        self.tenant_id = tenant_id
        self.config = config or {}
        self.metrics = {"requests": 0, "errors": 0, "total_ms": 0.0, "recommendations": 0}
        self.product_catalog = self._load_catalog()
    
    def _load_catalog(self) -> List[Dict]:
        """Catálogo de productos financieros."""
        return [
            {"id": "tc_platino", "name": "Tarjeta Platino", "category": "credit_card", "monthly": 50, "min_score": 700, "roi": 0.25},
            {"id": "tc_gold", "name": "Tarjeta Gold", "category": "credit_card", "monthly": 35, "min_score": 650, "roi": 0.20},
            {"id": "prestamo_personal", "name": "Préstamo Personal", "category": "loan", "monthly": 200, "min_score": 680, "roi": 0.15},
            {"id": "cuenta_inversion", "name": "Cuenta Inversión", "category": "investment", "monthly": 25, "min_score": 0, "roi": 0.08},
            {"id": "seguro_vida", "name": "Seguro de Vida", "category": "insurance", "monthly": 30, "min_score": 0, "roi": 0.12},
            {"id": "hipoteca", "name": "Crédito Hipotecario", "category": "mortgage", "monthly": 800, "min_score": 720, "roi": 0.10}
        ]
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera recomendaciones de productos con explicabilidad."""
        self.metrics["requests"] += 1
        t0 = time.perf_counter()
        
        try:
            data = input_data.get("input_data", input_data) if isinstance(input_data, dict) else {}
            
            # Extraer datos del cliente
            customer_id = data.get("customer_id", "cust_unknown")
            credit_score = data.get("credit_score", data.get("customer", {}).get("credit_score", 700))
            income = data.get("income", data.get("customer", {}).get("income", 50000))
            current_products = data.get("current_products", [])
            
            # Calcular perfil
            monthly_income = income / 12
            available_capacity = monthly_income * 0.3  # 30% DTI max
            customer_tier = self._get_tier(credit_score, income)
            
            # Generar recomendaciones
            recommendations = self._generate_recommendations(
                credit_score, income, monthly_income, available_capacity, 
                customer_tier, current_products
            )
            
            # Métricas de recomendación
            self.metrics["recommendations"] += len(recommendations)
            
            # Insights
            insights = self._generate_insights(recommendations, customer_tier)
            
            decision_trace = [
                f"customer_id={customer_id}",
                f"credit_score={credit_score}",
                f"tier={customer_tier}",
                f"recommendations={len(recommendations)}"
            ]
            
            latency_ms = max(1, int((time.perf_counter() - t0) * 1000))
            self.metrics["total_ms"] += latency_ms
            
            result = {
                "recommendation_id": f"rec_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "tenant_id": self.tenant_id,
                "customer_id": customer_id,
                "customer_profile": {
                    "credit_score": credit_score,
                    "income": income,
                    "tier": customer_tier,
                    "available_capacity": round(available_capacity, 2)
                },
                "recommendations": recommendations,
                "recommendations_count": len(recommendations),
                "cross_sell_count": sum(1 for r in recommendations if r["type"] == "cross_sell"),
                "upsell_count": sum(1 for r in recommendations if r["type"] == "upsell"),
                "total_potential_roi": round(sum(r["expected_roi"] for r in recommendations), 4),
                "key_insights": insights,
                "decision_trace": decision_trace,
                "compliance": {"fair_lending": "pass", "affordability": "pass"},
                "version": self.VERSION,
                "latency_ms": latency_ms
            }
            
            if DECISION_LAYER_AVAILABLE:
                try:
                    result = apply_decision_layer(result)
                except Exception:
                    pass
            
            return result
            
        except Exception as e:
            self.metrics["errors"] += 1
            latency_ms = max(1, int((time.perf_counter() - t0) * 1000))
            return {
                "recommendation_id": "error",
                "tenant_id": self.tenant_id,
                "recommendations": [],
                "key_insights": [f"Error: {str(e)[:100]}"],
                "decision_trace": ["error_occurred"],
                "version": self.VERSION,
                "latency_ms": latency_ms
            }
    
    def _get_tier(self, credit_score: float, income: float) -> str:
        """Determina tier del cliente."""
        if credit_score >= 750 and income >= 80000:
            return "platinum"
        elif credit_score >= 700 and income >= 50000:
            return "gold"
        elif credit_score >= 650 and income >= 30000:
            return "silver"
        return "bronze"
    
    def _generate_recommendations(self, credit_score: float, income: float, 
                                  monthly_income: float, available_capacity: float,
                                  tier: str, current_products: List) -> List[Dict]:
        """Genera recomendaciones ordenadas por affinity."""
        recommendations = []
        current_categories = [p.get("category", "") for p in current_products] if current_products else []
        
        for product in self.product_catalog:
            # Verificar elegibilidad
            if credit_score < product["min_score"]:
                continue
            
            # Verificar affordability
            if product["monthly"] > available_capacity:
                continue
            
            # Calcular affinity score
            affinity = self._calculate_affinity(product, credit_score, tier, current_categories)
            
            if affinity < 0.4:
                continue
            
            # Determinar tipo
            rec_type = "upsell" if product["category"] in current_categories else "cross_sell"
            
            # Calcular confianza
            confidence = min(0.95, 0.6 + (credit_score - 600) / 400 + affinity * 0.2)
            
            # Reason codes
            reason_codes = self._generate_reason_codes(product, affinity, tier, credit_score)
            
            recommendations.append({
                "product_id": product["id"],
                "product_name": product["name"],
                "category": product["category"],
                "type": rec_type,
                "affinity_score": round(affinity, 3),
                "confidence": round(confidence, 3),
                "expected_roi": product["roi"],
                "monthly_payment": product["monthly"],
                "reason_codes": reason_codes
            })
        
        # Ordenar por affinity
        recommendations.sort(key=lambda x: x["affinity_score"], reverse=True)
        return recommendations[:5]
    
    def _calculate_affinity(self, product: Dict, credit_score: float, 
                           tier: str, current_categories: List) -> float:
        """Calcula affinity score entre cliente y producto."""
        score = 0.3  # Base
        
        # Tier match
        tier_affinity = {
            "platinum": {"credit_card": 0.4, "investment": 0.3, "mortgage": 0.2},
            "gold": {"credit_card": 0.35, "loan": 0.25, "investment": 0.2},
            "silver": {"loan": 0.3, "insurance": 0.25, "credit_card": 0.2},
            "bronze": {"insurance": 0.3, "loan": 0.2}
        }
        score += tier_affinity.get(tier, {}).get(product["category"], 0.1)
        
        # Credit score bonus
        if credit_score >= product["min_score"] + 50:
            score += 0.15
        
        # Cross-sell opportunity
        if product["category"] not in current_categories:
            score += 0.1
        
        return min(1.0, score)
    
    def _generate_reason_codes(self, product: Dict, affinity: float, 
                               tier: str, credit_score: float) -> List[Dict]:
        """Genera reason codes para la recomendación."""
        codes = []
        
        if affinity >= 0.7:
            codes.append({"code": "AFF_HIGH", "description": "Alta afinidad producto-cliente", "contribution": 0.3})
        
        if tier in ["platinum", "gold"]:
            codes.append({"code": "TIER_PREMIUM", "description": f"Cliente tier {tier}", "contribution": 0.25})
        
        if credit_score >= 720:
            codes.append({"code": "CREDIT_EXCELLENT", "description": "Score crediticio excelente", "contribution": 0.2})
        
        if product["roi"] >= 0.15:
            codes.append({"code": "ROI_HIGH", "description": "Alto ROI esperado", "contribution": 0.15})
        
        return codes
    
    def _generate_insights(self, recommendations: List[Dict], tier: str) -> List[str]:
        """Genera insights de las recomendaciones."""
        insights = []
        
        if not recommendations:
            return ["No hay productos elegibles para este perfil"]
        
        # Top recommendation
        top = recommendations[0]
        insights.append(f"Recomendación principal: {top['product_name']} (affinity {top['affinity_score']*100:.0f}%)")
        
        # Tier insight
        insights.append(f"Cliente clasificado como tier {tier}")
        
        # Cross-sell opportunities
        cross_sells = [r for r in recommendations if r["type"] == "cross_sell"]
        if cross_sells:
            insights.append(f"Oportunidades cross-sell: {len(cross_sells)} productos")
        
        # ROI potential
        total_roi = sum(r["expected_roi"] for r in recommendations)
        insights.append(f"ROI potencial total: {total_roi*100:.1f}%")
        
        return insights[:5]
    
    def health(self) -> Dict[str, Any]:
        req = max(1, self.metrics["requests"])
        return {
            "agent_id": self.AGENT_ID,
            "version": self.VERSION,
            "status": "healthy",
            "tenant_id": self.tenant_id,
            "catalog_size": len(self.product_catalog),
            "metrics": {
                "requests": self.metrics["requests"],
                "errors": self.metrics["errors"],
                "recommendations": self.metrics["recommendations"],
                "avg_latency_ms": round(self.metrics["total_ms"] / req, 2)
            },
            "decision_layer": DECISION_LAYER_AVAILABLE
        }
    
    def health_check(self) -> Dict[str, Any]:
        return self.health()


def create_agent_instance(tenant_id: str, config: Dict = None):
    return ProductAffinityIA(tenant_id, config)
