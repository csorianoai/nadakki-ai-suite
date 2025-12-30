"""
NADAKKI AI SUITE - DASHBOARD METRICS v1.0.0 - TOP 1% EXECUTIVE
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
import logging

logger = logging.getLogger("NadakkiDashboardMetrics")
from decision_logger import DECISION_STORE, CHAIN_POSITION_BY_TENANT, LAST_HASH_BY_TENANT
from multitenant_integration import TENANTS_DB, PRICING_TIERS

def generate_top_reason(decisions: List[Dict]) -> str:
    if not decisions: return "No hay decisiones esta semana para analizar"
    decision_counts = {}
    for d in decisions:
        action = d.get("decision", {}).get("action", "UNKNOWN")
        decision_counts[action] = decision_counts.get(action, 0) + 1
    if not decision_counts: return "Procesando datos..."
    top_action = max(decision_counts, key=decision_counts.get)
    percentage = round(decision_counts[top_action] / len(decisions) * 100)
    explanations = {
        "ENRICH_AND_REANALYZE": f"El {percentage}% recomendaron enriquecer datos. Oportunidad de mejorar calidad de leads.",
        "ACTIVATE_ACQUISITION": f"El {percentage}% activaron adquisición. Pipeline saludable.",
        "REVIEW_REQUIRED": f"El {percentage}% requirieron revisión humana.",
        "EXECUTE_NOW": f"El {percentage}% fueron ejecuciones inmediatas. Alta confianza."
    }
    return explanations.get(top_action, f"El {percentage}% fueron {top_action}")

def detect_decision_drift(decisions: List[Dict]) -> Dict:
    if len(decisions) < 5: return {"detected": False, "message": "Datos insuficientes"}
    mid = len(decisions) // 2
    recent_conf = sum(d.get("decision", {}).get("confidence", 0) for d in decisions[:mid]) / mid
    older_conf = sum(d.get("decision", {}).get("confidence", 0) for d in decisions[mid:]) / (len(decisions) - mid)
    diff = recent_conf - older_conf
    if abs(diff) > 0.1:
        return {"detected": True, "direction": "up" if diff > 0 else "down", "magnitude": round(abs(diff)*100, 1),
                "message": f"Confianza {'subió' if diff > 0 else 'bajó'} {round(abs(diff)*100, 1)}%"}
    return {"detected": False, "message": "Patrones estables"}

def generate_risk_indicators(decisions: List[Dict]) -> List[Dict]:
    indicators = []
    if not decisions: return indicators
    confidences = [d.get("decision", {}).get("confidence", 0) for d in decisions]
    avg_conf = sum(confidences) / len(confidences)
    if avg_conf < 0.7:
        indicators.append({"type": "LOW_CONFIDENCE", "severity": "warning", "value": round(avg_conf, 2),
                          "message": f"Confianza promedio baja ({round(avg_conf*100)}%)"})
    high_value_low_conf = len([d for d in decisions if d.get("business_impact", {}).get("pipeline_value", 0) > 500000 
                               and d.get("decision", {}).get("confidence", 0) < 0.7])
    if high_value_low_conf > 0:
        indicators.append({"type": "HIGH_VALUE_RISK", "severity": "critical", "value": high_value_low_conf,
                          "message": f"{high_value_low_conf} decisiones alto valor + baja confianza"})
    return indicators

def get_authority_distribution(decisions: List[Dict]) -> Dict:
    dist = {"AI_AUTONOMOUS": 0, "AI_ASSISTED": 0, "HUMAN_IN_LOOP": 0}
    for d in decisions:
        mode = d.get("authority", {}).get("decision_mode", "UNKNOWN")
        if mode in dist: dist[mode] += 1
    total = sum(dist.values())
    return {"counts": dist, "autonomy_rate": round(dist["AI_AUTONOMOUS"]/total*100, 1) if total else 0}

def get_enhanced_dashboard_metrics(tenant_id: str) -> Dict:
    if tenant_id not in TENANTS_DB: raise ValueError(f"Tenant {tenant_id} not found")
    tenant = TENANTS_DB[tenant_id]
    plan = PRICING_TIERS.get(tenant["plan"], {})
    decisions = DECISION_STORE.get(tenant_id, [])
    sorted_decisions = sorted(decisions, key=lambda x: x.get("audit", {}).get("created_at", ""), reverse=True)
    
    now = datetime.utcnow()
    week_ago = (now - timedelta(days=7)).isoformat()
    decisions_week = [d for d in sorted_decisions if d.get("audit", {}).get("created_at", "") >= week_ago]
    
    confidences = [d.get("decision", {}).get("confidence", 0) for d in sorted_decisions]
    pipelines = [d.get("business_impact", {}).get("pipeline_value", 0) for d in sorted_decisions]
    
    decision_dist = {}
    for d in sorted_decisions:
        action = d.get("decision", {}).get("action", "UNKNOWN")
        decision_dist[action] = decision_dist.get(action, 0) + 1
    
    return {
        "tenant_id": tenant_id, "tenant_name": tenant["name"],
        "execution_boundary": f"tenant::{tenant_id}", "plan": plan.get("name"),
        "generated_at": now.isoformat() + "Z",
        "usage": {"decisions_used": tenant["billing"]["decisions_this_month"],
                  "decisions_limit": plan.get("decisions_per_month", 0)},
        "metrics": {
            "total_decisions": len(sorted_decisions),
            "decisions_this_week": len(decisions_week),
            "avg_confidence": round(sum(confidences)/len(confidences), 3) if confidences else 0,
            "total_pipeline": sum(pipelines),
            "decision_distribution": decision_dist
        },
        "chain": {"length": CHAIN_POSITION_BY_TENANT.get(tenant_id, 0),
                  "last_hash": LAST_HASH_BY_TENANT.get(tenant_id)},
        "authority": get_authority_distribution(sorted_decisions),
        "insights": {
            "top_reason": generate_top_reason(decisions_week),
            "drift_alert": detect_decision_drift(sorted_decisions),
            "risk_indicators": generate_risk_indicators(sorted_decisions)
        },
        "recent_decisions": [{"decision_id": d.get("decision_id"), "action": d.get("decision", {}).get("action"),
                              "confidence": d.get("decision", {}).get("confidence"),
                              "pipeline": d.get("business_impact", {}).get("pipeline_value")}
                             for d in sorted_decisions[:5]]
    }

enhanced_dashboard_router = APIRouter(prefix="/dashboard-v2", tags=["dashboard-v2"])

@enhanced_dashboard_router.get("/{tenant_id}/metrics")
async def api_enhanced_metrics(tenant_id: str):
    try: return get_enhanced_dashboard_metrics(tenant_id)
    except ValueError as e: raise HTTPException(404, str(e))

@enhanced_dashboard_router.get("/{tenant_id}/executive-summary")
async def api_executive_summary(tenant_id: str):
    try:
        m = get_enhanced_dashboard_metrics(tenant_id)
        return {"tenant_id": tenant_id,
                "summary": f"{m['metrics']['total_decisions']} decisiones, ${m['metrics']['total_pipeline']:,.0f} pipeline, {m['metrics']['avg_confidence']:.0%} confianza",
                "top_insight": m["insights"]["top_reason"]}
    except ValueError as e: raise HTTPException(404, str(e))

def register_enhanced_dashboard_routes(app):
    app.include_router(enhanced_dashboard_router)
    logger.info("Enhanced dashboard routes: /dashboard-v2")

__all__ = ["get_enhanced_dashboard_metrics", "enhanced_dashboard_router", "register_enhanced_dashboard_routes"]
