"""Analytics API Routes."""
from fastapi import APIRouter, HTTPException, Header, Query
from typing import Dict, Any
from ..services.analytics_service import analytics_service, ReportType

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/dashboard")
async def get_dashboard(x_tenant_id: str = Header(...), days: int = Query(30)) -> Dict[str, Any]:
    return analytics_service.get_dashboard_metrics(x_tenant_id, days)


@router.get("/comparison")
async def get_comparison(x_tenant_id: str = Header(...)) -> Dict[str, Any]:
    return analytics_service.get_performance_comparison(x_tenant_id)


@router.post("/reports")
async def generate_report(report_type: str = Query("weekly"), x_tenant_id: str = Header(...)) -> Dict[str, Any]:
    try: rt = ReportType(report_type)
    except: rt = ReportType.WEEKLY
    return analytics_service.generate_report(x_tenant_id, rt).to_dict()


@router.get("/reports")
async def list_reports(x_tenant_id: str = Header(...), limit: int = Query(10)) -> Dict[str, Any]:
    reports = analytics_service.list_reports(x_tenant_id, limit)
    return {"reports": [r.to_dict() for r in reports], "total": len(reports)}


@router.get("/reports/{report_id}")
async def get_report(report_id: str) -> Dict[str, Any]:
    report = analytics_service.get_report(report_id)
    if not report: raise HTTPException(status_code=404, detail="Report not found")
    return report.to_dict()
