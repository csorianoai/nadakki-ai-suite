"""Scheduler Service - APScheduler para publicación automática."""
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)


class SchedulerService:
    """Servicio de programación de tareas."""
    
    _instance: Optional["SchedulerService"] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        self._initialized = True
        logger.info("SchedulerService initialized")
    
    def start(self) -> Dict[str, Any]:
        if self.is_running:
            return {"status": "already_running"}
        
        self.scheduler.add_job(self._publish_scheduled, IntervalTrigger(minutes=5), id="publish_campaigns", replace_existing=True)
        self.scheduler.add_job(self._sync_metrics, IntervalTrigger(hours=1), id="sync_metrics", replace_existing=True)
        self.scheduler.add_job(self._refresh_tokens, IntervalTrigger(hours=6), id="refresh_tokens", replace_existing=True)
        
        self.scheduler.start()
        self.is_running = True
        logger.info("Scheduler started")
        return {"status": "started", "jobs": self.get_jobs()}
    
    def stop(self) -> Dict[str, Any]:
        if not self.is_running:
            return {"status": "not_running"}
        self.scheduler.shutdown(wait=False)
        self.is_running = False
        return {"status": "stopped"}
    
    def get_jobs(self) -> list:
        return [{"id": j.id, "next_run": j.next_run_time.isoformat() if j.next_run_time else None} for j in self.scheduler.get_jobs()]
    
    def get_status(self) -> Dict[str, Any]:
        return {"is_running": self.is_running, "jobs_count": len(self.scheduler.get_jobs()) if self.is_running else 0}
    
    def _publish_scheduled(self):
        logger.info("Running publish_scheduled job")
    
    def _sync_metrics(self):
        logger.info("Running sync_metrics job")
    
    def _refresh_tokens(self):
        logger.info("Running refresh_tokens job")


scheduler_service = SchedulerService()
