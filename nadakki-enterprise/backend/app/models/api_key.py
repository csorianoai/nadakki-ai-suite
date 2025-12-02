from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from app.models.base import Base, TimestampMixin, generate_id
from datetime import datetime

class APIKey(Base, TimestampMixin):
    __tablename__ = "api_keys"
    
    id = Column(String(36), primary_key=True, default=generate_id)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    key = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255))
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    def is_valid(self) -> bool:
        if not self.is_active:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True
    
    def __repr__(self):
        return f"<APIKey {self.name}>"
