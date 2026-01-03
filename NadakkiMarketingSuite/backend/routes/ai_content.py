"""AI Content API Routes."""
from fastapi import APIRouter, HTTPException, Header, Query
from typing import Dict, Any, Optional
from pydantic import BaseModel
from ..services.ai_content_service import ai_content_service, ContentTone

router = APIRouter(prefix="/api/v1/ai", tags=["ai-content"])


class GenerateContentRequest(BaseModel):
    prompt: str
    tone: str = "professional"
    platform: str = "facebook"
    max_length: int = 280
    include_hashtags: bool = True


class GenerateFromTemplateRequest(BaseModel):
    template_id: str
    variables: Dict[str, str]
    platform: str = "facebook"


@router.get("/templates")
async def list_templates(category: Optional[str] = Query(None), platform: Optional[str] = Query(None)) -> Dict[str, Any]:
    templates = ai_content_service.get_templates(category, platform)
    return {"templates": [{"id": t.id, "name": t.name, "category": t.category, "variables": t.variables, "platforms": t.platforms} for t in templates], "total": len(templates)}


@router.post("/generate")
async def generate_content(data: GenerateContentRequest, x_tenant_id: str = Header(...)) -> Dict[str, Any]:
    try: tone = ContentTone(data.tone)
    except: tone = ContentTone.PROFESSIONAL
    content = ai_content_service.generate_ai_content(tenant_id=x_tenant_id, prompt=data.prompt, tone=tone, platform=data.platform, max_length=data.max_length, include_hashtags=data.include_hashtags)
    return content.to_dict()


@router.post("/generate/template")
async def generate_from_template(data: GenerateFromTemplateRequest, x_tenant_id: str = Header(...)) -> Dict[str, Any]:
    content = ai_content_service.generate_from_template(tenant_id=x_tenant_id, template_id=data.template_id, variables=data.variables, platform=data.platform)
    if not content: raise HTTPException(status_code=404, detail="Template not found")
    return content.to_dict()


@router.get("/suggestions")
async def get_suggestions(x_tenant_id: str = Header(...)) -> Dict[str, Any]:
    return {"suggestions": ai_content_service.get_content_suggestions(x_tenant_id)}


@router.get("/history")
async def get_history(x_tenant_id: str = Header(...), limit: int = Query(20)) -> Dict[str, Any]:
    contents = ai_content_service.list_generated_content(x_tenant_id, limit)
    return {"contents": [c.to_dict() for c in contents], "total": len(contents)}
