from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Tenant

router = APIRouter(prefix="/api/v1/tenants", tags=["tenants"])

@router.get("/{tenant_id}")
async def get_tenant(tenant_id: str, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant.to_dict()

@router.get("")
async def list_tenants(db: Session = Depends(get_db)):
    tenants = db.query(Tenant).all()
    return [t.to_dict() for t in tenants]

@router.patch("/{tenant_id}")
async def update_tenant(tenant_id: str, data: dict, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    for key, value in data.items():
        if hasattr(tenant, key) and not key.startswith("_"):
            setattr(tenant, key, value)
    db.commit()
    return tenant.to_dict()
