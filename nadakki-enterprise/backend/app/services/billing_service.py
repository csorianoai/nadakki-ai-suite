from sqlalchemy.orm import Session
from app.models import Subscription

class BillingService:
    @staticmethod
    def create_subscription(tenant_id: str, plan: str, db: Session):
        sub = Subscription(
            tenant_id=tenant_id,
            plan=plan,
            stripe_customer_id="cus_pending",
            stripe_subscription_id="sub_pending",
            status="pending_payment"
        )
        db.add(sub)
        db.commit()
        return sub
    
    @staticmethod
    def get_subscription(tenant_id: str, db: Session):
        return db.query(Subscription).filter(Subscription.tenant_id == tenant_id).first()
