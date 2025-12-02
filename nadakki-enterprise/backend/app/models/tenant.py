from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import JSON
from app.models.base import Base, TimestampMixin, generate_id

class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"
    
    id = Column(String(36), primary_key=True, default=generate_id)
    api_key = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    country = Column(String(2), nullable=False)
    region = Column(String(50))
    industry = Column(String(100))
    plan = Column(String(50), default="starter", nullable=False)
    stripe_customer_id = Column(String(255), unique=True)
    stripe_subscription_id = Column(String(255), unique=True)
    is_active = Column(Boolean, default=False)
    compliance_reviewed = Column(Boolean, default=False)
    gdpr_compliant = Column(Boolean, default=False)
    aml_risk_score = Column(String(50))
    branding = Column(JSON, nullable=True)
    custom_domain = Column(String(255), nullable=True, unique=True)
    
    def __repr__(self):
        return f"<Tenant {self.name} ({self.plan})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "plan": self.plan,
            "is_active": self.is_active,
            "country": self.country,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
