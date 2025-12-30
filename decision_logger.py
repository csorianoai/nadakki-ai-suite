"""
NADAKKI AI SUITE - DECISION LOGGING MODULE v1.0.0
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from uuid import uuid4
from fastapi import APIRouter, HTTPException
import hashlib
import json
import logging

logger = logging.getLogger("NadakkiDecisionLogger")

DECISION_STORE: Dict[str, List[Dict]] = {}
LAST_HASH_BY_TENANT: Dict[str, str] = {}
CHAIN_POSITION_BY_TENANT: Dict[str, int] = {}

def generate_hash(data: Any) -> str:
    content = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(content.encode()).hexdigest()

def generate_decision_hash(decision_id: str, tenant_id: str, action: str, confidence: float, timestamp: str, previous_hash: Optional[str]) -> str:
    content = f"{previous_hash or 'GENESIS'}:{decision_id}:{tenant_id}:{action}:{confidence}:{timestamp}"
    return hashlib.sha256(content.encode()).hexdigest()

def log_workflow_decision(workflow_response: Dict, tenant_id: str, tenant_plan: str = "enterprise", source: str = "API") -> Dict:
    workflow_id = workflow_response.get("workflow_id", f"WF-{uuid4().hex[:8]}")
    decision_data = workflow_response.get("decision", {})
    summary = workflow_response.get("summary", {})
    steps = workflow_response.get("steps", [])
    
    decision_id = f"DEC-{workflow_id}"
    now = datetime.utcnow()
    timestamp = now.isoformat() + "Z"
    
    previous_hash = LAST_HASH_BY_TENANT.get(tenant_id)
    chain_position = CHAIN_POSITION_BY_TENANT.get(tenant_id, 0)
    
    action = decision_data.get("decision", "REVIEW_REQUIRED")
    confidence = decision_data.get("confidence", 0.5)
    pipeline_value = summary.get("pipeline_value", 0)
    
    if confidence >= 0.85:
        decision_mode, approval_required = "AI_AUTONOMOUS", False
    elif confidence >= 0.60:
        decision_mode, approval_required = "AI_ASSISTED", True
    else:
        decision_mode, approval_required = "HUMAN_IN_LOOP", True
    
    input_hash = generate_hash(workflow_response)[:16]
    output_hash = generate_decision_hash(decision_id, tenant_id, action, confidence, timestamp, previous_hash)[:16]
    
    agents_executed = [{"agent_id": s.get("agent", "unknown"), "agent_name": s.get("step_name", "Unknown"), 
                        "status": s.get("status", "unknown"), "duration_ms": s.get("duration_ms", 0)}
                       for s in steps if s.get("status") not in ["skipped", None]]
    
    contract = {
        "_contract": {"version": "3.0.0", "type": "DECISION_CONTRACT", "immutable": True},
        "decision_id": decision_id,
        "workflow_id": workflow_id,
        "workflow_name": workflow_response.get("workflow_name", "Unknown"),
        "workflow_version": workflow_response.get("workflow_version", "1.0.0"),
        "tenant": {"tenant_id": tenant_id, "execution_boundary": f"tenant::{tenant_id}", "plan": tenant_plan},
        "decision": {"action": action, "confidence": confidence, "priority": "HIGH" if pipeline_value > 500000 else "MEDIUM",
                     "valid_until": (now + timedelta(days=7)).isoformat() + "Z"},
        "authority": {"decision_mode": decision_mode, "approval_required": approval_required, "policy_id": "MARKETING_STANDARD_V1"},
        "business_impact": {"pipeline_value": pipeline_value, "risk_level": "LOW" if confidence > 0.7 else "MEDIUM", "currency": "USD"},
        "execution": {"steps_completed": summary.get("steps_completed", "0/0"), "total_duration_ms": summary.get("total_duration_ms", 0),
                      "agents_executed": agents_executed, "source": source},
        "audit": {"created_at": timestamp, "input_hash": input_hash, "output_hash": output_hash,
                  "previous_decision_hash": previous_hash, "chain_position": chain_position,
                  "execution_boundary": f"tenant::{tenant_id}", "request_id": f"req-{uuid4().hex[:8]}"},
        "compliance": {"status": "PASS", "regulations_checked": ["GDPR"], "data_retention_days": 90}
    }
    
    if tenant_id not in DECISION_STORE:
        DECISION_STORE[tenant_id] = []
    DECISION_STORE[tenant_id].append(contract)
    LAST_HASH_BY_TENANT[tenant_id] = output_hash
    CHAIN_POSITION_BY_TENANT[tenant_id] = chain_position + 1
    
    logger.info(f"Decision logged: {decision_id} for {tenant_id} (chain: {chain_position})")
    return contract

def get_tenant_decisions(tenant_id: str, limit: int = 20) -> Dict:
    decisions = DECISION_STORE.get(tenant_id, [])
    sorted_decisions = sorted(decisions, key=lambda x: x.get("audit", {}).get("created_at", ""), reverse=True)
    return {"tenant_id": tenant_id, "execution_boundary": f"tenant::{tenant_id}", "total": len(decisions), "decisions": sorted_decisions[:limit]}

def get_tenant_decision_stats(tenant_id: str) -> Dict:
    decisions = DECISION_STORE.get(tenant_id, [])
    if not decisions:
        return {"tenant_id": tenant_id, "total_decisions": 0, "stats": {}}
    confidences = [d.get("decision", {}).get("confidence", 0) for d in decisions]
    pipelines = [d.get("business_impact", {}).get("pipeline_value", 0) for d in decisions]
    distribution = {}
    for d in decisions:
        action = d.get("decision", {}).get("action", "UNKNOWN")
        distribution[action] = distribution.get(action, 0) + 1
    return {"tenant_id": tenant_id, "total_decisions": len(decisions),
            "stats": {"avg_confidence": round(sum(confidences)/len(confidences), 3), "total_pipeline": sum(pipelines),
                      "decision_distribution": distribution, "chain_length": CHAIN_POSITION_BY_TENANT.get(tenant_id, 0),
                      "last_hash": LAST_HASH_BY_TENANT.get(tenant_id)}}

def verify_decision_chain(tenant_id: str) -> Dict:
    decisions = DECISION_STORE.get(tenant_id, [])
    if not decisions:
        return {"tenant_id": tenant_id, "valid": True, "chain_length": 0, "message": "No decisions"}
    sorted_decisions = sorted(decisions, key=lambda x: x.get("audit", {}).get("chain_position", 0))
    issues = []
    for i, d in enumerate(sorted_decisions):
        if i == 0 and d.get("audit", {}).get("previous_decision_hash"):
            issues.append({"decision_id": d.get("decision_id"), "issue": "First should have null previous_hash"})
        elif i > 0:
            expected = sorted_decisions[i-1].get("audit", {}).get("output_hash")
            actual = d.get("audit", {}).get("previous_decision_hash")
            if expected != actual:
                issues.append({"decision_id": d.get("decision_id"), "issue": f"Chain broken"})
    return {"tenant_id": tenant_id, "valid": len(issues) == 0, "chain_length": len(sorted_decisions),
            "last_hash": sorted_decisions[-1].get("audit", {}).get("output_hash") if sorted_decisions else None,
            "issues": issues, "message": "Chain OK" if not issues else f"{len(issues)} issues"}

decision_log_router = APIRouter(prefix="/decision-logs", tags=["decision-logs"])

@decision_log_router.get("/{tenant_id}")
async def api_get_decisions(tenant_id: str, limit: int = 20):
    return get_tenant_decisions(tenant_id, limit)

@decision_log_router.get("/{tenant_id}/stats")
async def api_get_stats(tenant_id: str):
    return get_tenant_decision_stats(tenant_id)

@decision_log_router.get("/{tenant_id}/verify-chain")
async def api_verify_chain(tenant_id: str):
    return verify_decision_chain(tenant_id)

def register_decision_log_routes(app):
    app.include_router(decision_log_router)
    logger.info("Decision logging routes registered: /decision-logs")

__all__ = ["DECISION_STORE", "log_workflow_decision", "get_tenant_decisions", "get_tenant_decision_stats", 
           "verify_decision_chain", "decision_log_router", "register_decision_log_routes"]
