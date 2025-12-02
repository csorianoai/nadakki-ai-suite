from sqlalchemy import Column, String, Integer, Text, ForeignKey
from app.models.base import Base, TimestampMixin, generate_id

class AgentExecution(Base, TimestampMixin):
    __tablename__ = "agent_executions"
    
    id = Column(String(36), primary_key=True, default=generate_id)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_name = Column(String(255), nullable=False)
    agent_type = Column(String(100))
    input_data = Column(Text)
    output_data = Column(Text)
    status = Column(String(50))
    error_message = Column(Text, nullable=True)
    duration_ms = Column(Integer)
    tokens_used = Column(Integer)
    cost_cents = Column(Integer)
    
    def __repr__(self):
        return f"<AgentExecution {self.agent_name} - {self.status}>"
