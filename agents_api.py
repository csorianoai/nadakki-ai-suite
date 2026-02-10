"""
NADAKKI AI Suite - Agents API
FastAPI backend para exponer agentes operativos y esqueletos
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import json
from pathlib import Path
from datetime import datetime

app = FastAPI(
    title="NADAKKI Agents API",
    description="API para gestionar agentes operativos y esqueletos",
    version="1.0.0"
)

# Cargar datos del análisis
REPORT_PATH = Path("agent_verification/detailed_verification_report.json")
if not REPORT_PATH.exists():
    raise FileNotFoundError(f"Reporte no encontrado: {REPORT_PATH}")

with open(REPORT_PATH, 'r', encoding='utf-8') as f:
    REPORT = json.load(f)

class AgentsResponse(BaseModel):
    total: int
    agents: List[Dict]
    metadata: Dict

# Datos procesados
OPERATIONAL_AGENTS = [agent for agent in REPORT['detailed_analysis'] if agent['final_category'] == 'AGENTE_OPERATIVO']
SKELETON_AGENTS = [agent for agent in REPORT['detailed_analysis'] if agent['final_category'] == 'ESQUELETO_AGENTE']
UTILITY_SCRIPTS = [agent for agent in REPORT['detailed_analysis'] if agent['final_category'] == 'UTILIDAD_SCRIPT']

TOP_5_SKELETONS = sorted([a for a in SKELETON_AGENTS if a['score'] >= 60], key=lambda x: x['score'], reverse=True)[:5]
TOP_9_SKELETONS = sorted([a for a in SKELETON_AGENTS if a['score'] >= 60], key=lambda x: x['score'], reverse=True)[:9]

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat(), "operational_agents": len(OPERATIONAL_AGENTS), "skeleton_agents": len(SKELETON_AGENTS), "utility_scripts": len(UTILITY_SCRIPTS)}

@app.get("/api/summary")
async def get_summary():
    return {"total_agents": len(OPERATIONAL_AGENTS), "total_skeletons": len(SKELETON_AGENTS), "total_utilities": len(UTILITY_SCRIPTS), "total_files": len(REPORT['detailed_analysis']), "avg_score_operational": round(sum(a['score'] for a in OPERATIONAL_AGENTS) / len(OPERATIONAL_AGENTS), 2), "avg_score_skeleton": round(sum(a['score'] for a in SKELETON_AGENTS) / len(SKELETON_AGENTS), 2), "top_5_ready": len(TOP_5_SKELETONS), "top_9_ready": len(TOP_9_SKELETONS), "generated_at": REPORT['metadata']['generated_at']}

@app.get("/api/agents/operational", response_model=AgentsResponse)
async def get_operational_agents(module: Optional[str] = Query(None), min_score: float = Query(0)):
    agents = [a for a in OPERATIONAL_AGENTS if a['score'] >= min_score]
    if module:
        agents = [a for a in agents if a['module'].lower() == module.lower()]
    return AgentsResponse(total=len(agents), agents=agents, metadata={"status": "OPERATIONAL", "category": "AGENTE_OPERATIVO", "module_filter": module, "score_filter": min_score})

@app.get("/api/agents/operational/by-module")
async def get_operational_by_module():
    by_module = {}
    for agent in OPERATIONAL_AGENTS:
        module = agent['module']
        if module not in by_module:
            by_module[module] = []
        by_module[module].append({"filename": agent['filename'], "score": agent['score'], "lines": agent['lines']})
    return {"total_modules": len(by_module), "total_agents": len(OPERATIONAL_AGENTS), "by_module": by_module}

@app.get("/api/agents/skeletons", response_model=AgentsResponse)
async def get_skeleton_agents(module: Optional[str] = Query(None), min_score: float = Query(50), ready_to_implement: bool = Query(False)):
    agents = [a for a in SKELETON_AGENTS if a['score'] >= min_score]
    if ready_to_implement:
        agents = [a for a in agents if a['score'] >= 60]
    if module:
        agents = [a for a in agents if a['module'].lower() == module.lower()]
    return AgentsResponse(total=len(agents), agents=agents, metadata={"status": "SKELETON", "category": "ESQUELETO_AGENTE", "min_score": min_score, "ready_to_implement": ready_to_implement, "module_filter": module})

@app.get("/api/agents/skeletons/top-5")
async def get_top_5_skeletons():
    return {"total": len(TOP_5_SKELETONS), "priority": "HIGH - Implementar primero", "estimated_days_total": 300, "agents": TOP_5_SKELETONS}

@app.get("/api/agents/skeletons/top-9")
async def get_top_9_skeletons():
    return {"total": len(TOP_9_SKELETONS), "priority": "HIGH - Implementar gradualmente", "estimated_days_total": 540, "agents": TOP_9_SKELETONS}

@app.get("/api/agents/{agent_id}")
async def get_agent_details(agent_id: str):
    for agent in REPORT['detailed_analysis']:
        if agent['filename'] == agent_id or agent['relative_path'] == agent_id:
            return {"agent": agent, "status_explanation": {"AGENTE_OPERATIVO": "Operativo - Listo para producción", "ESQUELETO_AGENTE": "Esqueleto - Requiere implementación", "UTILIDAD_SCRIPT": "Utilidad - Mantener como script auxiliar"}.get(agent['final_category'], "Desconocido")}
    raise HTTPException(status_code=404, detail=f"Agente no encontrado: {agent_id}")

@app.get("/api/agents/statistics")
async def get_statistics():
    return {"operational": {"count": len(OPERATIONAL_AGENTS), "avg_score": round(sum(a['score'] for a in OPERATIONAL_AGENTS) / len(OPERATIONAL_AGENTS), 2)}, "skeletons": {"count": len(SKELETON_AGENTS), "avg_score": round(sum(a['score'] for a in SKELETON_AGENTS) / len(SKELETON_AGENTS), 2), "ready_to_implement": len(TOP_9_SKELETONS)}, "utilities": {"count": len(UTILITY_SCRIPTS)}, "total_files": len(REPORT['detailed_analysis'])}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
