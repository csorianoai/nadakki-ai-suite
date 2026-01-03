"""Nadakki Marketing Suite API v4.1 - Day 4 (AI + Analytics)."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys

sys.path.insert(0, "..")
from .routes import campaigns_router, connections_router, scheduler_router, metrics_router, tenants_router, ai_content_router, analytics_router, export_router, notifications_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Nadakki Marketing Suite v4.1")
    yield
    from .services.scheduler_service import scheduler_service
    if scheduler_service.is_running: scheduler_service.stop()


app = FastAPI(title="Nadakki Marketing Suite", description="Multi-Tenant Marketing Platform with AI", version="4.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(campaigns_router)
app.include_router(connections_router)
app.include_router(scheduler_router)
app.include_router(metrics_router)
app.include_router(tenants_router)
app.include_router(ai_content_router)
app.include_router(analytics_router)
app.include_router(export_router)
app.include_router(notifications_router)


@app.get("/")
async def root():
    return {"service": "Nadakki Marketing Suite", "version": "4.1.0", "day": 4, "features": ["multi-tenant", "ai-content", "analytics", "export", "notifications"]}


@app.get("/health")
async def health():
    from .services.scheduler_service import scheduler_service
    return {"status": "healthy", "scheduler": scheduler_service.is_running}
