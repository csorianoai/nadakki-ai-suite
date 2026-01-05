from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

router = APIRouter(prefix="/api/templates", tags=["templates"])

TEMPLATES_DB = {
    "t1": {"id": "t1", "name": "Onboarding Completo", "description": "Secuencia de 7 emails para nuevos usuarios", "category": "onboarding", "channels": ["email", "push"], "duration": "14 dias", "difficulty": "Facil", "effectiveness": 92, "users": 12500, "starred": True, "metrics": {"open_rate": 78, "click_rate": 45, "conversion": 28}},
    "t2": {"id": "t2", "name": "Nurturing Educativo", "description": "Educa a leads con contenido de valor", "category": "nurturing", "channels": ["email", "sms"], "duration": "30 dias", "difficulty": "Medio", "effectiveness": 85, "users": 8400, "starred": True, "metrics": {"open_rate": 72, "click_rate": 38, "conversion": 22}},
    "t3": {"id": "t3", "name": "Lanzamiento Producto", "description": "Campana completa para lanzamiento", "category": "promotional", "channels": ["email", "sms", "push"], "duration": "10 dias", "difficulty": "Avanzado", "effectiveness": 88, "users": 15600, "starred": False, "metrics": {"open_rate": 68, "click_rate": 42, "conversion": 31}},
    "t4": {"id": "t4", "name": "Prevencion Churn", "description": "Detecta y retiene usuarios en riesgo", "category": "retention", "channels": ["email", "sms"], "duration": "21 dias", "difficulty": "Medio", "effectiveness": 76, "users": 5200, "starred": True, "metrics": {"open_rate": 65, "click_rate": 28, "conversion": 18}},
    "t5": {"id": "t5", "name": "Win-back Agresivo", "description": "Recupera usuarios inactivos", "category": "winback", "channels": ["email", "sms"], "duration": "7 dias", "difficulty": "Facil", "effectiveness": 64, "users": 9200, "starred": False, "metrics": {"open_rate": 58, "click_rate": 24, "conversion": 12}},
    "t6": {"id": "t6", "name": "Black Friday", "description": "Campana de ventas estacional", "category": "promotional", "channels": ["email", "sms", "push"], "duration": "5 dias", "difficulty": "Avanzado", "effectiveness": 94, "users": 22400, "starred": True, "metrics": {"open_rate": 82, "click_rate": 51, "conversion": 38}},
}

@router.get("")
async def list_templates(category: Optional[str] = None, starred: Optional[bool] = None, sort_by: str = "effectiveness"):
    templates = list(TEMPLATES_DB.values())
    if category and category != "all":
        templates = [t for t in templates if t["category"] == category]
    if starred is not None:
        templates = [t for t in templates if t["starred"] == starred]
    if sort_by == "effectiveness":
        templates.sort(key=lambda x: x["effectiveness"], reverse=True)
    elif sort_by == "users":
        templates.sort(key=lambda x: x["users"], reverse=True)
    return {
        "templates": templates,
        "total": len(templates),
        "categories": {"all": len(TEMPLATES_DB), "onboarding": 1, "nurturing": 1, "promotional": 2, "retention": 1, "winback": 1}
    }

@router.get("/{template_id}")
async def get_template(template_id: str):
    template = TEMPLATES_DB.get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.post("/{template_id}/use")
async def use_template(template_id: str, tenant_id: str = Query(...)):
    template = TEMPLATES_DB.get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    template["users"] += 1
    return {"message": f"Template '{template['name']}' ready", "journey_config": {"name": f"Journey from {template['name']}", "channels": template["channels"]}}

@router.post("/{template_id}/star")
async def toggle_star(template_id: str):
    template = TEMPLATES_DB.get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    template["starred"] = not template["starred"]
    return {"starred": template["starred"]}
