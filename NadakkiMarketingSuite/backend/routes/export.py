"""Export API Routes."""
from fastapi import APIRouter, HTTPException, Header, Query
from fastapi.responses import Response
from typing import Dict, Any
from ..services.export_service import export_service, ExportFormat

router = APIRouter(prefix="/api/v1/export", tags=["export"])


@router.get("/formats")
async def list_formats() -> Dict[str, Any]:
    return {"formats": export_service.get_export_formats()}


@router.get("/campaigns")
async def export_campaigns(format: str = Query("csv"), x_tenant_id: str = Header(...)) -> Response:
    try: fmt = ExportFormat(format)
    except: raise HTTPException(status_code=400, detail=f"Invalid format: {format}")
    result = export_service.export_campaigns(x_tenant_id, fmt)
    if "error" in result: raise HTTPException(status_code=400, detail=result["error"])
    content_type = "text/csv" if fmt == ExportFormat.CSV else "application/json"
    return Response(content=result["content"], media_type=content_type, headers={"Content-Disposition": f"attachment; filename=campaigns.{format}"})


@router.get("/reports/{report_id}")
async def export_report(report_id: str, format: str = Query("json")) -> Response:
    try: fmt = ExportFormat(format)
    except: raise HTTPException(status_code=400, detail=f"Invalid format: {format}")
    result = export_service.export_analytics_report(report_id, fmt)
    if "error" in result: raise HTTPException(status_code=404, detail=result["error"])
    return Response(content=result["content"], media_type="application/json", headers={"Content-Disposition": f"attachment; filename=report.{format}"})
