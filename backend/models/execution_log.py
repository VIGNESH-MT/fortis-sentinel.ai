"""
FORTIS SENTINEL - Execution Log Model

Records every action taken by a governed agent, including timing,
resources accessed, and outcomes. Critical for audit compliance.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship

from database import Base


class ExecutionLog(Base):
    """
    SQLAlchemy model for agent execution logs.

    Captures every action performed by an agent, providing a complete
    audit trail of agent behavior for governance and compliance purposes.

    Attributes:
        id: Unique log entry identifier (UUID).
        agent_id: Reference to the agent that performed the action.
        timestamp: When the action occurred.
        action: Description of the action taken.
        resource_accessed: What resource was accessed (e.g., database, API).
        status: Outcome status (success, failure, blocked, timeout).
        result: Action result or error message.
        duration_ms: Execution time in milliseconds.
        created_at: Log entry creation timestamp.
    """

    __tablename__ = "execution_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    action = Column(String(255), nullable=False)
    resource_accessed = Column(String(255), nullable=True)
    status = Column(String(50), nullable=True)
    result = Column(Text, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    agent = relationship("Agent", back_populates="execution_logs")

    __table_args__ = (
        Index("idx_logs_agent_time", "agent_id", "timestamp"),
    )

    def to_dict(self) -> dict:
        """Serialize execution log to dictionary."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "action": self.action,
            "resource_accessed": self.resource_accessed,
            "status": self.status,
            "result": self.result,
            "duration_ms": self.duration_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
