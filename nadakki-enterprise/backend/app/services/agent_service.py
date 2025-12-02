from sqlalchemy.orm import Session
from app.models import AgentExecution

class AgentService:
    @staticmethod
    def create_execution(tenant_id: str, agent_name: str, input_data: dict, db: Session):
        execution = AgentExecution(
            tenant_id=tenant_id,
            agent_name=agent_name,
            input_data=str(input_data),
            status="pending"
        )
        db.add(execution)
        db.commit()
        return execution
    
    @staticmethod
    def get_execution(execution_id: str, db: Session):
        return db.query(AgentExecution).filter(AgentExecution.id == execution_id).first()
