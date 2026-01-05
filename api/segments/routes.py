from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/segments", tags=["segments"])

# ═══════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════

class SegmentRule(BaseModel):
    field: str
    operator: str
    value: str

class Segment(BaseModel):
    id: Optional[str] = None
    tenant_id: str = "credicefi"
    name: str
    description: str = ""
    type: str = "dynamic"  # dynamic, static, rfm, predictive
    rules: List[SegmentRule] = []
    user_count: int = 0
    growth_rate: float = 0.0
    avg_value: float = 0.0
    status: str = "active"  # active, inactive
    tags: List[str] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class SegmentCreate(BaseModel):
    name: str
    description: str = ""
    type: str = "dynamic"
    rules: List[dict] = []
    tags: List[str] = []

# ═══════════════════════════════════════════════════════════════
# IN-MEMORY DATABASE
# ═══════════════════════════════════════════════════════════════

segments_db: dict[str, List[Segment]] = {
    "credicefi": [
        Segment(
            id="seg-1", tenant_id="credicefi", name="All Users",
            description="All registered users", type="static",
            user_count=125000, growth_rate=2.5, avg_value=85.50,
            status="active", tags=["all"],
            created_at="2024-01-01T00:00:00Z", updated_at="2024-01-15T00:00:00Z"
        ),
        Segment(
            id="seg-2", tenant_id="credicefi", name="Active Users (30 days)",
            description="Users active in the last 30 days", type="dynamic",
            rules=[SegmentRule(field="last_activity", operator="within", value="30d")],
            user_count=45000, growth_rate=5.2, avg_value=120.00,
            status="active", tags=["active", "engagement"],
            created_at="2024-01-01T00:00:00Z", updated_at="2024-02-01T00:00:00Z"
        ),
        Segment(
            id="seg-3", tenant_id="credicefi", name="New Users (7 days)",
            description="Users registered in the last 7 days", type="dynamic",
            rules=[SegmentRule(field="created_at", operator="within", value="7d")],
            user_count=8500, growth_rate=12.8, avg_value=0.00,
            status="active", tags=["new", "onboarding"],
            created_at="2024-01-01T00:00:00Z", updated_at="2024-02-01T00:00:00Z"
        ),
        Segment(
            id="seg-4", tenant_id="credicefi", name="At Risk of Churn",
            description="Users showing churn signals", type="predictive",
            rules=[SegmentRule(field="churn_score", operator="greater_than", value="0.7")],
            user_count=12000, growth_rate=-3.5, avg_value=95.00,
            status="active", tags=["churn", "retention"],
            created_at="2024-01-15T00:00:00Z", updated_at="2024-02-01T00:00:00Z"
        ),
        Segment(
            id="seg-5", tenant_id="credicefi", name="VIP Customers",
            description="Top spending customers", type="rfm",
            rules=[SegmentRule(field="total_spend", operator="greater_than", value="1000")],
            user_count=3200, growth_rate=8.5, avg_value=2500.00,
            status="active", tags=["vip", "high-value"],
            created_at="2024-01-01T00:00:00Z", updated_at="2024-02-01T00:00:00Z"
        ),
        Segment(
            id="seg-6", tenant_id="credicefi", name="Highly Engaged",
            description="Users with high engagement scores", type="dynamic",
            rules=[SegmentRule(field="engagement_score", operator="greater_than", value="80")],
            user_count=28000, growth_rate=4.2, avg_value=150.00,
            status="active", tags=["engaged", "active"],
            created_at="2024-01-01T00:00:00Z", updated_at="2024-02-01T00:00:00Z"
        ),
        Segment(
            id="seg-7", tenant_id="credicefi", name="Cart Abandoners",
            description="Users who abandoned cart in last 7 days", type="dynamic",
            rules=[SegmentRule(field="cart_abandoned", operator="within", value="7d")],
            user_count=5600, growth_rate=1.8, avg_value=75.00,
            status="active", tags=["cart", "recovery"],
            created_at="2024-01-15T00:00:00Z", updated_at="2024-02-01T00:00:00Z"
        ),
        Segment(
            id="seg-8", tenant_id="credicefi", name="Mobile Users",
            description="Users primarily using mobile app", type="dynamic",
            rules=[SegmentRule(field="primary_device", operator="equals", value="mobile")],
            user_count=67000, growth_rate=6.5, avg_value=95.00,
            status="active", tags=["mobile", "app"],
            created_at="2024-01-01T00:00:00Z", updated_at="2024-02-01T00:00:00Z"
        ),
    ]
}

# ═══════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════

@router.get("")
async def get_segments(
    tenant_id: str = Query("credicefi"),
    type: Optional[str] = None,
    status: Optional[str] = None
):
    """Get all segments for a tenant"""
    segments = segments_db.get(tenant_id, [])
    
    if type:
        segments = [s for s in segments if s.type == type]
    if status:
        segments = [s for s in segments if s.status == status]
    
    return {
        "segments": [s.dict() for s in segments],
        "total": len(segments),
        "total_users": sum(s.user_count for s in segments)
    }

@router.get("/stats/summary")
async def get_segments_stats(tenant_id: str = Query("credicefi")):
    """Get segments statistics summary"""
    segments = segments_db.get(tenant_id, [])
    
    return {
        "summary": {
            "total_segments": len(segments),
            "active_segments": len([s for s in segments if s.status == "active"]),
            "total_users": sum(s.user_count for s in segments),
            "dynamic_segments": len([s for s in segments if s.type == "dynamic"]),
            "predictive_segments": len([s for s in segments if s.type == "predictive"]),
            "rfm_segments": len([s for s in segments if s.type == "rfm"]),
            "avg_segment_size": round(sum(s.user_count for s in segments) / len(segments)) if segments else 0,
            "avg_growth_rate": round(sum(s.growth_rate for s in segments) / len(segments), 1) if segments else 0,
        }
    }

@router.get("/{segment_id}")
async def get_segment(segment_id: str, tenant_id: str = Query("credicefi")):
    """Get a single segment by ID"""
    segments = segments_db.get(tenant_id, [])
    segment = next((s for s in segments if s.id == segment_id), None)
    
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    
    return segment.dict()

@router.post("")
async def create_segment(segment: SegmentCreate, tenant_id: str = Query("credicefi")):
    """Create a new segment"""
    if tenant_id not in segments_db:
        segments_db[tenant_id] = []
    
    new_segment = Segment(
        id=f"seg-{uuid.uuid4().hex[:8]}",
        tenant_id=tenant_id,
        name=segment.name,
        description=segment.description,
        type=segment.type,
        rules=[SegmentRule(**r) for r in segment.rules] if segment.rules else [],
        user_count=0,
        growth_rate=0.0,
        avg_value=0.0,
        status="active",
        tags=segment.tags,
        created_at=datetime.utcnow().isoformat() + "Z",
        updated_at=datetime.utcnow().isoformat() + "Z"
    )
    
    segments_db[tenant_id].append(new_segment)
    
    return {"message": "Segment created", "segment": new_segment.dict()}

@router.put("/{segment_id}")
async def update_segment(
    segment_id: str,
    updates: dict,
    tenant_id: str = Query("credicefi")
):
    """Update a segment"""
    segments = segments_db.get(tenant_id, [])
    segment_idx = next((i for i, s in enumerate(segments) if s.id == segment_id), None)
    
    if segment_idx is None:
        raise HTTPException(status_code=404, detail="Segment not found")
    
    segment = segments[segment_idx]
    segment_dict = segment.dict()
    
    for key, value in updates.items():
        if key in segment_dict and key not in ["id", "tenant_id", "created_at"]:
            segment_dict[key] = value
    
    segment_dict["updated_at"] = datetime.utcnow().isoformat() + "Z"
    segments[segment_idx] = Segment(**segment_dict)
    
    return {"message": "Segment updated", "segment": segments[segment_idx].dict()}

@router.post("/{segment_id}/refresh")
async def refresh_segment(segment_id: str, tenant_id: str = Query("credicefi")):
    """Refresh segment user count"""
    segments = segments_db.get(tenant_id, [])
    segment_idx = next((i for i, s in enumerate(segments) if s.id == segment_id), None)
    
    if segment_idx is None:
        raise HTTPException(status_code=404, detail="Segment not found")
    
    # Simulate refresh with random increase/decrease
    import random
    change = random.randint(-500, 1000)
    segments[segment_idx].user_count = max(0, segments[segment_idx].user_count + change)
    segments[segment_idx].updated_at = datetime.utcnow().isoformat() + "Z"
    
    return {"message": "Segment refreshed", "segment": segments[segment_idx].dict()}

@router.delete("/{segment_id}")
async def delete_segment(segment_id: str, tenant_id: str = Query("credicefi")):
    """Delete a segment"""
    segments = segments_db.get(tenant_id, [])
    segment_idx = next((i for i, s in enumerate(segments) if s.id == segment_id), None)
    
    if segment_idx is None:
        raise HTTPException(status_code=404, detail="Segment not found")
    
    deleted = segments.pop(segment_idx)
    
    return {"message": "Segment deleted", "segment_id": deleted.id}
