from sqlalchemy.orm import Session
from app.models import Tenant
from app.models.base import generate_id

class TenantService:
    @staticmethod
    def create_tenant(email: str, name: str, country: str, db: Session):
        tenant = Tenant(
            email=email,
            name=name,
            country=country,
            api_key=f"ndk_{generate_id()}"
        )
        db.add(tenant)
        db.commit()
        return tenant
    
    @staticmethod
    def get_tenant(tenant_id: str, db: Session):
        return db.query(Tenant).filter(Tenant.id == tenant_id).first()
    
    @staticmethod
    def list_tenants(db: Session):
        return db.query(Tenant).all()
