"""
SQLAlchemy ORM models for the multi-tenant schema.
All tenant-scoped tables include tenant_id FK to tenants.
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=True)
    plan = Column(String, default="starter")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", back_populates="tenant")
    oauth_tokens = relationship("OAuthToken", back_populates="tenant")
    agent_executions = relationship("AgentExecution", back_populates="tenant")
    audit_events = relationship("AuditEvent", back_populates="tenant")
    config = relationship("TenantConfig", back_populates="tenant", uselist=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    email = Column(String, nullable=False)
    role = Column(String, default="viewer")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tenant = relationship("Tenant", back_populates="users")


class OAuthToken(Base):
    __tablename__ = "oauth_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    platform = Column(String(50), nullable=False)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tenant = relationship("Tenant", back_populates="oauth_tokens")


class AgentExecution(Base):
    __tablename__ = "agent_executions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    agent_id = Column(String, nullable=False, index=True)
    dry_run = Column(Boolean, default=True)
    result = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tenant = relationship("Tenant", back_populates="agent_executions")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(String, nullable=True)
    action = Column(String, nullable=True)
    endpoint = Column(String, nullable=True)
    method = Column(String(10), nullable=True)
    status_code = Column(Integer, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    tenant = relationship("Tenant", back_populates="audit_events")


class TenantConfig(Base):
    __tablename__ = "tenant_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, unique=True)
    meta_live_enabled = Column(Boolean, default=False)
    sendgrid_live_enabled = Column(Boolean, default=False)

    tenant = relationship("Tenant", back_populates="config")
