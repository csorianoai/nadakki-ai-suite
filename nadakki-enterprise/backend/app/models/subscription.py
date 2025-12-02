from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from app.models.base import Base, TimestampMixin, generate_id

class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"
    
    id = Column(String(36), primary_key=True, default=generate_id)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    stripe_customer_id = Column(String(255), nullable=False, unique=True)
    stripe_subscription_id = Column(String(255), nullable=False, unique=True)
    stripe_product_id = Column(String(255))
    plan = Column(String(50), nullable=False)
    status = Column(String(50), default="active")
    monthly_requests_limit = Column(Integer)
    requests_used_this_month = Column(Integer, default=0)
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    trial_ends_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Subscription {self.tenant_id} - {self.plan}>"
