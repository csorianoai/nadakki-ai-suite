"""
Analytics Router - Real-time metrics and KPIs
NADAKKI AI Suite v2.0
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import random
import uuid

router = APIRouter(prefix="/analytics", tags=["Analytics"])

# ═══════════════════════════════════════════════════════════════
# MODELOS PYDANTIC
# ═══════════════════════════════════════════════════════════════

class MetricValue(BaseModel):
    current: float
    previous: float
    change: float
    trend: str  # "up", "down", "stable"

class KPI(BaseModel):
    id: str
    name: str
    value: float
    target: float
    unit: str
    category: str

class CampaignPerformance(BaseModel):
    id: str
    name: str
    status: str
    sent: int
    delivered: int
    opened: int
    clicked: int
    converted: int
    revenue: float
    ctr: float
    conversion_rate: float

class OverviewResponse(BaseModel):
    tenant_id: str
    period: str
    generated_at: datetime
    mau: MetricValue
    dau: MetricValue
    new_users: MetricValue
    stickiness: MetricValue
    daily_sessions: MetricValue
    sessions_per_mau: MetricValue
    active_campaigns: int
    total_revenue: MetricValue
    kpis: List[KPI]
    top_campaigns: List[CampaignPerformance]

class TimeSeriesPoint(BaseModel):
    date: str
    value: float

class PerformanceChartData(BaseModel):
    metric: str
    data: List[TimeSeriesPoint]
    total: float
    average: float

# ═══════════════════════════════════════════════════════════════
# BASE DE DATOS EN MEMORIA (Simula persistencia real)
# ═══════════════════════════════════════════════════════════════

class AnalyticsDB:
    """Simulated analytics database with realistic data generation"""
    
    def __init__(self):
        self.events = []
        self.sessions = []
        self.users = {}
        self._seed_data()
    
    def _seed_data(self):
        """Generate realistic seed data"""
        base_mau = 45000
        base_dau = 8500
        
        # Generate 90 days of historical data
        for i in range(90):
            date = datetime.now() - timedelta(days=89-i)
            daily_users = base_dau + random.randint(-500, 800) + (i * 15)
            sessions = daily_users * random.uniform(2.5, 3.5)
            
            self.sessions.append({
                "date": date.strftime("%Y-%m-%d"),
                "users": daily_users,
                "sessions": int(sessions),
                "new_users": int(daily_users * random.uniform(0.05, 0.12)),
                "events": int(sessions * random.uniform(8, 15))
            })
    
    def get_metrics(self, tenant_id: str, days: int = 30) -> dict:
        """Calculate real metrics from data"""
        recent = self.sessions[-days:]
        previous = self.sessions[-(days*2):-days] if len(self.sessions) >= days*2 else self.sessions[:days]
        
        current_dau = sum(s["users"] for s in recent) / len(recent)
        previous_dau = sum(s["users"] for s in previous) / len(previous) if previous else current_dau
        
        current_sessions = sum(s["sessions"] for s in recent) / len(recent)
        previous_sessions = sum(s["sessions"] for s in previous) / len(previous) if previous else current_sessions
        
        current_new = sum(s["new_users"] for s in recent)
        previous_new = sum(s["new_users"] for s in previous) if previous else current_new
        
        # Calculate MAU (unique users in period)
        current_mau = int(current_dau * 5.3)  # Approximation based on DAU
        previous_mau = int(previous_dau * 5.3)
        
        return {
            "mau": {"current": current_mau, "previous": previous_mau},
            "dau": {"current": int(current_dau), "previous": int(previous_dau)},
            "sessions": {"current": int(current_sessions), "previous": int(previous_sessions)},
            "new_users": {"current": current_new, "previous": previous_new},
            "stickiness": {"current": round((current_dau / current_mau) * 100, 1), "previous": round((previous_dau / previous_mau) * 100, 1)},
            "sessions_per_mau": {"current": round(current_sessions / current_mau * 30, 2), "previous": round(previous_sessions / previous_mau * 30, 2)},
            "time_series": recent
        }

# Instancia global
analytics_db = AnalyticsDB()

# ═══════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@router.get("/overview", response_model=OverviewResponse)
async def get_analytics_overview(
    tenant_id: str = Query(default="default", description="Tenant ID"),
    period: str = Query(default="30d", description="Time period: 24h, 7d, 30d, 90d")
):
    """
    Get complete marketing analytics overview.
    Returns MAU, DAU, sessions, campaigns performance, and KPIs.
    """
    days_map = {"24h": 1, "7d": 7, "30d": 30, "90d": 90}
    days = days_map.get(period, 30)
    
    metrics = analytics_db.get_metrics(tenant_id, days)
    
    def calc_metric(data: dict) -> MetricValue:
        change = ((data["current"] - data["previous"]) / data["previous"] * 100) if data["previous"] else 0
        return MetricValue(
            current=data["current"],
            previous=data["previous"],
            change=round(change, 1),
            trend="up" if change > 0 else "down" if change < 0 else "stable"
        )
    
    # Generate realistic KPIs
    kpis = [
        KPI(id="cac", name="Customer Acquisition Cost", value=45.20, target=40.00, unit="USD", category="acquisition"),
        KPI(id="ltv", name="Customer Lifetime Value", value=580.00, target=600.00, unit="USD", category="retention"),
        KPI(id="nps", name="Net Promoter Score", value=72, target=75, unit="points", category="satisfaction"),
        KPI(id="churn", name="Churn Rate", value=2.3, target=2.0, unit="%", category="retention"),
        KPI(id="arr", name="Annual Recurring Revenue", value=2450000, target=2500000, unit="USD", category="revenue"),
        KPI(id="arpu", name="Average Revenue Per User", value=125.50, target=130.00, unit="USD", category="revenue"),
    ]
    
    # Generate top campaigns performance
    campaigns = [
        CampaignPerformance(
            id=str(uuid.uuid4())[:8],
            name="Welcome Series Q1",
            status="active",
            sent=45230, delivered=44500, opened=18900, clicked=4200, converted=890,
            revenue=89000.00, ctr=9.4, conversion_rate=4.7
        ),
        CampaignPerformance(
            id=str(uuid.uuid4())[:8],
            name="Cart Abandonment",
            status="active", 
            sent=12450, delivered=12300, opened=6800, clicked=2100, converted=520,
            revenue=52000.00, ctr=17.1, conversion_rate=7.5
        ),
        CampaignPerformance(
            id=str(uuid.uuid4())[:8],
            name="Black Friday Promo",
            status="completed",
            sent=89200, delivered=88500, opened=42000, clicked=15200, converted=3800,
            revenue=380000.00, ctr=17.2, conversion_rate=9.0
        ),
        CampaignPerformance(
            id=str(uuid.uuid4())[:8],
            name="Re-engagement Wave",
            status="active",
            sent=8900, delivered=8750, opened=2100, clicked=450, converted=95,
            revenue=9500.00, ctr=5.1, conversion_rate=2.1
        ),
    ]
    
    return OverviewResponse(
        tenant_id=tenant_id,
        period=period,
        generated_at=datetime.now(),
        mau=calc_metric(metrics["mau"]),
        dau=calc_metric(metrics["dau"]),
        new_users=calc_metric(metrics["new_users"]),
        stickiness=calc_metric(metrics["stickiness"]),
        daily_sessions=calc_metric(metrics["sessions"]),
        sessions_per_mau=calc_metric(metrics["sessions_per_mau"]),
        active_campaigns=len([c for c in campaigns if c.status == "active"]),
        total_revenue=MetricValue(current=530500.00, previous=485000.00, change=9.4, trend="up"),
        kpis=kpis,
        top_campaigns=campaigns
    )

@router.get("/performance")
async def get_performance_chart(
    tenant_id: str = Query(default="default"),
    metric: str = Query(default="sessions", description="sessions, users, events, revenue"),
    period: str = Query(default="30d")
):
    """Get time series data for performance charts"""
    days_map = {"24h": 1, "7d": 7, "30d": 30, "90d": 90}
    days = days_map.get(period, 30)
    
    metrics = analytics_db.get_metrics(tenant_id, days)
    time_series = metrics["time_series"]
    
    data = []
    for day in time_series:
        value = day.get(metric, day.get("sessions", 0))
        data.append(TimeSeriesPoint(date=day["date"], value=value))
    
    total = sum(d.value for d in data)
    average = total / len(data) if data else 0
    
    return PerformanceChartData(
        metric=metric,
        data=data,
        total=round(total, 2),
        average=round(average, 2)
    )

@router.get("/realtime")
async def get_realtime_metrics(tenant_id: str = Query(default="default")):
    """Get real-time metrics (last 5 minutes)"""
    return {
        "active_users": random.randint(120, 180),
        "sessions_per_minute": random.randint(15, 35),
        "events_per_minute": random.randint(80, 150),
        "top_pages": [
            {"path": "/dashboard", "users": random.randint(20, 40)},
            {"path": "/products", "users": random.randint(15, 30)},
            {"path": "/checkout", "users": random.randint(10, 25)},
        ],
        "top_events": [
            {"name": "page_view", "count": random.randint(100, 200)},
            {"name": "button_click", "count": random.randint(50, 100)},
            {"name": "form_submit", "count": random.randint(10, 30)},
        ],
        "timestamp": datetime.now().isoformat()
    }

@router.post("/events")
async def track_event(
    tenant_id: str,
    event_name: str,
    event_data: Dict[str, Any] = {}
):
    """Track analytics event"""
    event = {
        "id": str(uuid.uuid4()),
        "tenant_id": tenant_id,
        "event_name": event_name,
        "event_data": event_data,
        "timestamp": datetime.now().isoformat()
    }
    analytics_db.events.append(event)
    return {"success": True, "event_id": event["id"]}
