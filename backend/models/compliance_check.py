"""
FORTIS SENTINEL - Compliance Check Model

Records compliance evaluations conducted against regulatory frameworks
such as the EU AI Act, Colorado AI Act, and Singapore MGF.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, Float, ForeignKey, Index
from sqlalchemy.orm import relationship

from database import Base


class ComplianceCheck(Base):
    """
    SQLAlchemy model for compliance check results.

    Each record represents a point-in-time evaluation of an agent's
    compliance with a specific regulatory framework.

    Attributes:
        id: Unique check identifier (UUID).
        agent_id: Reference to the evaluated agent.
        framework: Regulatory framework name.
        status: Overall compliance status (compliant, partial, non_compliant).
        score: Numeric compliance score (0.0-100.0).
        findings: JSON findings detail.
        recommendations: JSON list of recommended remediations.
        checked_at: When the check was performed.
    """

    __tablename__ = "compliance_checks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    framework = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    score = Column(Float, nullable=True, default=0.0)
    findings = Column(Text, nullable=True)  # JSON string
    recommendations = Column(Text, nullable=True)  # JSON string
    checked_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    agent = relationship("Agent", back_populates="compliance_checks")

    __table_args__ = (
        Index("idx_comp_agent", "agent_id"),
        Index("idx_comp_framework", "framework"),
        Index("idx_comp_status", "status"),
    )

    def to_dict(self) -> dict:
        """Serialize compliance check to dictionary."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "framework": self.framework,
            "status": self.status,
            "score": self.score,
            "findings": self.findings,
            "recommendations": self.recommendations,
            "checked_at": self.checked_at.isoformat() if self.checked_at else None,
        }
