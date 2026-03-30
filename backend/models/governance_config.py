"""
FORTIS SENTINEL - Governance Configuration Model

Stores governance policies that constrain agent behavior.
Policies are attached to specific agents and enforced in real-time.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship

from database import Base


class GovernanceConfig(Base):
    """
    SQLAlchemy model for governance policy configurations.

    Each governance config defines a set of rules applied to a specific
    agent.  Policies can be toggled active/inactive and support multiple
    enforcement levels.

    Attributes:
        id: Unique config identifier (UUID).
        agent_id: Reference to the governed agent.
        policy_name: Human-readable policy name.
        policy_type: Category (safety, compliance, operational, ethical).
        rules: JSON rules definition.
        enforcement_level: Severity of enforcement (advisory, warning, blocking).
        is_active: Whether the policy is currently enforced.
        created_at: Policy creation timestamp.
        updated_at: Last modification timestamp.
    """

    __tablename__ = "governance_configs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    policy_name = Column(String(255), nullable=False)
    policy_type = Column(String(50), nullable=False, default="safety")
    rules = Column(Text, nullable=True)  # JSON string
    enforcement_level = Column(String(50), nullable=False, default="warning")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    agent = relationship("Agent", back_populates="governance_configs")

    __table_args__ = (
        Index("idx_gov_agent", "agent_id"),
        Index("idx_gov_type", "policy_type"),
        Index("idx_gov_active", "is_active"),
    )

    def to_dict(self) -> dict:
        """Serialize governance config to dictionary."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "policy_name": self.policy_name,
            "policy_type": self.policy_type,
            "rules": self.rules,
            "enforcement_level": self.enforcement_level,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
