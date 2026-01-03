"""Scheduler API Routes."""
from fastapi import APIRouter
from ..services.scheduler_service import scheduler_service

router = APIRouter(prefix="/api/v1/scheduler", tags=["scheduler"])

@router.post("/start")
async def start_scheduler():
    return scheduler_service.start()

@router.post("/stop")
async def stop_scheduler():
    return scheduler_service.stop()

@router.get("/status")
async def get_status():
    return scheduler_service.get_status()

@router.get("/jobs")
async def list_jobs():
    return {"jobs": scheduler_service.get_jobs()}
