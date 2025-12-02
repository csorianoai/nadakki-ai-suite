from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Subscription

router = APIRouter(prefix="/api/v1/billing", tags=["billing"])

@router.get("/subscription/{tenant_id}")
async def get_subscription(tenant_id: str, db: Session = Depends(get_db)):
    sub = db.query(Subscription).filter(Subscription.tenant_id == tenant_id).first()
    if not sub:
        return {"status": "no_subscription"}
    return {"plan": sub.plan, "status": sub.status}

@router.post("/subscription/{tenant_id}")
async def create_subscription(tenant_id: str, plan: str, db: Session = Depends(get_db)):
    sub = Subscription(
        tenant_id=tenant_id,
        plan=plan,
        stripe_customer_id="cus_pending",
        stripe_subscription_id="sub_pending",
        status="pending_payment"
    )
    db.add(sub)
    db.commit()
    return {"subscription_id": str(sub.id), "status": "pending_payment"}
