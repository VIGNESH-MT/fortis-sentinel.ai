"""
FORTIS SENTINEL - Anomaly Model

Represents anomalies detected by the mathematical governance engines.
Each anomaly is linked to a specific agent and scored by severity and confidence.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, Float, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship

from database import Base


class Anomaly(Base):
    """
    SQLAlchemy model for detected anomalies.

    Anomalies are flagged by FORTIS governance engines when an agent's
    behavior deviates from expected patterns, violates contracts, or
    triggers cascade risk thresholds.

    Attributes:
        id: Unique anomaly identifier (UUID).
        agent_id: Reference to the agent that triggered the anomaly.
        detected_at: Timestamp of anomaly detection.
        anomaly_type: Category (trajectory_deviation, contract_violation,
                      cascade_risk, boundary_breach, alignment_drift,
                      goal_hijack_attempt).
        severity: Severity level (low, medium, high, critical).
        confidence: Engine confidence in the detection (0.0-1.0).
        description: Human-readable anomaly description.
        framework_source: Which of the 15 approaches detected this.
        raw_metrics: JSON blob with the raw mathematical metrics.
        resolved: Whether the anomaly has been resolved.
        resolved_at: When it was resolved (nullable).
    """

    __tablename__ = "anomalies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    detected_at = Column(DateTime, default=datetime.utcnow)
    anomaly_type = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False, default="medium")
    confidence = Column(Float, nullable=False, default=0.0)
    description = Column(Text, nullable=True)
    framework_source = Column(String(100), nullable=True)
    raw_metrics = Column(Text, nullable=True)  # JSON string for portability
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    agent = relationship("Agent", back_populates="anomalies")

    __table_args__ = (
        Index("idx_anomalies_agent", "agent_id"),
        Index("idx_anomalies_severity", "severity"),
        Index("idx_anomalies_type", "anomaly_type"),
        Index("idx_anomalies_resolved", "resolved"),
    )

    def to_dict(self) -> dict:
        """Serialize anomaly to dictionary."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
            "anomaly_type": self.anomaly_type,
            "severity": self.severity,
            "confidence": self.confidence,
            "description": self.description,
            "framework_source": self.framework_source,
            "raw_metrics": self.raw_metrics,
            "resolved": self.resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }
