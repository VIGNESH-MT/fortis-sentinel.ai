"""
FORTIS SENTINEL - Agent Model

Represents an AI agent registered in the governance platform.
Tracks agent identity, capabilities, status, and health metrics.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, Float, Index
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.orm import relationship

from database import Base


class Agent(Base):
    """
    SQLAlchemy model for AI agents registered with FORTIS SENTINEL.

    Each agent has a unique identity within its organization, a set of allowed
    and forbidden actions, and a governance status.

    Attributes:
        id: Unique agent identifier (UUID).
        org_id: Organization identifier for multi-tenant isolation.
        name: Human-readable agent name, unique within org.
        description: Detailed description of agent purpose.
        model_type: Underlying AI model (e.g., 'gpt-4', 'claude-3').
        status: Current agent status (active, paused, quarantined, decommissioned).
        allowed_actions: JSON list of permitted actions.
        forbidden_actions: JSON list of explicitly forbidden actions.
        risk_score: Current computed risk score (0.0-1.0).
        health_score: Current health score (0.0-1.0).
        created_at: Agent registration timestamp.
        updated_at: Last modification timestamp.
    """

    __tablename__ = "agents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String(36), nullable=False, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    model_type = Column(String(100), nullable=True)
    status = Column(String(50), default="active", nullable=False)
    allowed_actions = Column(SQLiteJSON, nullable=True, default=list)
    forbidden_actions = Column(SQLiteJSON, nullable=True, default=list)
    risk_score = Column(Float, default=0.0)
    health_score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    execution_logs = relationship("ExecutionLog", back_populates="agent", cascade="all, delete-orphan")
    anomalies = relationship("Anomaly", back_populates="agent", cascade="all, delete-orphan")
    governance_configs = relationship("GovernanceConfig", back_populates="agent", cascade="all, delete-orphan")
    compliance_checks = relationship("ComplianceCheck", back_populates="agent", cascade="all, delete-orphan")
    audit_entries = relationship("AuditTrail", back_populates="agent", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_agents_org", "org_id"),
        Index("idx_agents_status", "status"),
    )

    def to_dict(self) -> dict:
        """Serialize agent to dictionary."""
        return {
            "id": self.id,
            "org_id": self.org_id,
            "name": self.name,
            "description": self.description,
            "model_type": self.model_type,
            "status": self.status,
            "allowed_actions": self.allowed_actions or [],
            "forbidden_actions": self.forbidden_actions or [],
            "risk_score": float(self.risk_score) if self.risk_score else 0.0,
            "health_score": float(self.health_score) if self.health_score else 1.0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
