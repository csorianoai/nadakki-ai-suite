"""Advanced Analytics Service - Reportes y tendencias."""
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class ReportType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


@dataclass
class AnalyticsReport:
    id: str
    tenant_id: str
    report_type: ReportType
    start_date: datetime
    end_date: datetime
    metrics: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "tenant_id": self.tenant_id,
            "report_type": self.report_type.value,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "metrics": self.metrics, "insights": self.insights,
            "recommendations": self.recommendations,
            "created_at": self.created_at.isoformat()
        }


class AnalyticsService:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._reports: Dict[str, AnalyticsReport] = {}
    
    def get_dashboard_metrics(self, tenant_id: str, days: int = 30) -> Dict[str, Any]:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        return {
            "summary": {
                "total_campaigns": 24, "active_campaigns": 8, "total_posts": 156,
                "total_engagement": 45230, "total_reach": 234500, "avg_engagement_rate": 4.2
            },
            "trends": {
                "engagement": self._generate_trend_data(days, 1000, 200),
                "reach": self._generate_trend_data(days, 5000, 1000)
            },
            "by_platform": {
                "facebook": {"engagement": 15000, "reach": 80000},
                "instagram": {"engagement": 20000, "reach": 95000},
                "linkedin": {"engagement": 5000, "reach": 35000}
            },
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()}
        }
    
    def _generate_trend_data(self, days: int, base: int, variance: int) -> List[Dict]:
        data = []
        current = datetime.utcnow() - timedelta(days=days)
        for i in range(days):
            data.append({"date": current.strftime("%Y-%m-%d"), "value": base + random.randint(-variance, variance)})
            current += timedelta(days=1)
        return data
    
    def generate_report(self, tenant_id: str, report_type: ReportType, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> AnalyticsReport:
        if not end_date: end_date = datetime.utcnow()
        if not start_date:
            days = {"daily": 1, "weekly": 7, "monthly": 30}.get(report_type.value, 7)
            start_date = end_date - timedelta(days=days)
        
        metrics = self.get_dashboard_metrics(tenant_id, (end_date - start_date).days)
        insights = ["✅ Engagement rate por encima del promedio (4.2%).", "🏆 Instagram es tu mejor plataforma."]
        recommendations = ["📌 Aumenta frecuencia en LinkedIn.", "🎯 Usa contenido IA para consistencia."]
        
        report = AnalyticsReport(
            id=str(uuid.uuid4()), tenant_id=tenant_id, report_type=report_type,
            start_date=start_date, end_date=end_date, metrics=metrics,
            insights=insights, recommendations=recommendations
        )
        self._reports[report.id] = report
        return report
    
    def get_report(self, report_id: str) -> Optional[AnalyticsReport]:
        return self._reports.get(report_id)
    
    def list_reports(self, tenant_id: str, limit: int = 10) -> List[AnalyticsReport]:
        reports = [r for r in self._reports.values() if r.tenant_id == tenant_id]
        return sorted(reports, key=lambda x: x.created_at, reverse=True)[:limit]
    
    def get_performance_comparison(self, tenant_id: str) -> Dict[str, Any]:
        return {
            "engagement": {"current": 45230, "previous": 38500, "change": 17.6},
            "reach": {"current": 234500, "previous": 211000, "change": 11.1}
        }


analytics_service = AnalyticsService()
