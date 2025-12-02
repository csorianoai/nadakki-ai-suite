from sqlalchemy import Column, String, Boolean, ForeignKey, UniqueConstraint
from app.models.base import Base, TimestampMixin, generate_id

class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_id)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    job_title = Column(String(255))
    phone = Column(String(20))
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (UniqueConstraint('tenant_id', 'email', name='uq_tenant_user_email'),)
    
    def __repr__(self):
        return f"<User {self.email}>"
