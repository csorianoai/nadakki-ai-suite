from sqlalchemy import Column, String, Text, ForeignKey
from app.models.base import Base, TimestampMixin, generate_id

class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=generate_id)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(255), nullable=False)
    resource = Column(String(255))
    resource_id = Column(String(255))
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    status = Column(String(50))
    error_message = Column(Text, nullable=True)
    details = Column(Text)
    
    def __repr__(self):
        return f"<AuditLog {self.action} - {self.status}>"
