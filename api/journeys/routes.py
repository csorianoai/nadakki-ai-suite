from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/journeys", tags=["journeys"])

class JourneyNode(BaseModel):
    id: str
    type: str
    title: str
    description: str
    config: Dict[str, Any] = {}
    position: Dict[str, float]

class JourneyConnection(BaseModel):
    id: str
    from_node: str
    to_node: str
    label: Optional[str] = None

class JourneyCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    nodes: List[JourneyNode] = []
    connections: List[JourneyConnection] = []

class Journey(BaseModel):
    id: str
    tenant_id: str
    name: str
    description: str
    status: str
    nodes: List[JourneyNode]
    connections: List[JourneyConnection]
    stats: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

JOURNEYS_DB: Dict[str, Dict] = {}

def init_sample_journeys():
    JOURNEYS_DB["journey-onboarding-001"] = {
        "id": "journey-onboarding-001",
        "tenant_id": "credicefi",
        "name": "Customer Onboarding Journey",
        "description": "Secuencia de bienvenida para nuevos usuarios",
        "status": "active",
        "nodes": [
            {"id": "node-1", "type": "trigger", "title": "Usuario se registra", "description": "Nuevo registro", "config": {"event": "user.signup"}, "position": {"x": 100, "y": 200}},
            {"id": "node-2", "type": "email", "title": "Email Bienvenida", "description": "Enviar bienvenida", "config": {"template": "welcome"}, "position": {"x": 350, "y": 200}},
            {"id": "node-3", "type": "wait", "title": "Esperar 2 dias", "description": "Pausa 48h", "config": {"duration": 2, "unit": "days"}, "position": {"x": 600, "y": 200}},
        ],
        "connections": [
            {"id": "conn-1", "from_node": "node-1", "to_node": "node-2"},
            {"id": "conn-2", "from_node": "node-2", "to_node": "node-3"},
        ],
        "stats": {"contacts": 1250, "completed": 856, "conversion_rate": 68.5},
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

init_sample_journeys()

@router.get("")
async def list_journeys(tenant_id: str = Query(...), status: Optional[str] = None, limit: int = 20):
    journeys = [j for j in JOURNEYS_DB.values() if j["tenant_id"] == tenant_id]
    if status:
        journeys = [j for j in journeys if j["status"] == status]
    return {"journeys": journeys[:limit], "total": len(journeys)}

@router.get("/{journey_id}")
async def get_journey(journey_id: str, tenant_id: str = Query(...)):
    journey = JOURNEYS_DB.get(journey_id)
    if not journey or journey["tenant_id"] != tenant_id:
        raise HTTPException(status_code=404, detail="Journey not found")
    return journey

@router.post("")
async def create_journey(data: JourneyCreate, tenant_id: str = Query(...)):
    journey_id = f"journey-{uuid.uuid4().hex[:8]}"
    journey = {
        "id": journey_id, "tenant_id": tenant_id, "name": data.name,
        "description": data.description or "", "status": "draft",
        "nodes": [n.dict() for n in data.nodes],
        "connections": [c.dict() for c in data.connections],
        "stats": {"contacts": 0, "completed": 0, "conversion_rate": 0},
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    JOURNEYS_DB[journey_id] = journey
    return {"id": journey_id, "message": "Journey created", "journey": journey}

@router.put("/{journey_id}")
async def update_journey(journey_id: str, data: dict, tenant_id: str = Query(...)):
    journey = JOURNEYS_DB.get(journey_id)
    if not journey or journey["tenant_id"] != tenant_id:
        raise HTTPException(status_code=404, detail="Journey not found")
    journey.update(data)
    journey["updated_at"] = datetime.now().isoformat()
    return {"message": "Journey updated", "journey": journey}

@router.post("/{journey_id}/activate")
async def activate_journey(journey_id: str, tenant_id: str = Query(...)):
    journey = JOURNEYS_DB.get(journey_id)
    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found")
    journey["status"] = "active"
    return {"message": "Journey activated", "status": "active"}

@router.post("/{journey_id}/pause")
async def pause_journey(journey_id: str, tenant_id: str = Query(...)):
    journey = JOURNEYS_DB.get(journey_id)
    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found")
    journey["status"] = "paused"
    return {"message": "Journey paused", "status": "paused"}

@router.delete("/{journey_id}")
async def delete_journey(journey_id: str, tenant_id: str = Query(...)):
    if journey_id in JOURNEYS_DB:
        del JOURNEYS_DB[journey_id]
    return {"message": "Journey deleted"}

@router.get("/{journey_id}/stats")
async def get_journey_stats(journey_id: str, tenant_id: str = Query(...)):
    journey = JOURNEYS_DB.get(journey_id)
    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found")
    return {"journey_id": journey_id, "stats": journey["stats"]}
