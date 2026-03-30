"""
FORTIS SENTINEL - Audit Trail Model

Implements a cryptographic hash-chain audit trail using Merkle-style
linked hashes. Each entry is immutably linked to its predecessor,
guaranteeing tamper-evidence for regulatory compliance.
"""

from __future__ import annotations

import uuid
import hashlib
import json
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship

from database import Base


class AuditTrail(Base):
    """
    SQLAlchemy model for the cryptographic audit trail.

    Each audit entry is hashed and linked to the previous entry's hash,
    forming an immutable chain similar to a blockchain.  This satisfies
    Approach 13 (Cryptographic Audit Trail) requirements.

    Attributes:
        id: Unique entry identifier (UUID).
        agent_id: Reference to the agent associated with this event.
        event_type: Type of event (action, governance_check, compliance_check,
                    anomaly_detected, policy_change, status_change).
        event_data: JSON blob with event details.
        hash: SHA-256 hash of this entry (id + event_type + event_data + previous_hash + timestamp).
        previous_hash: Hash of the preceding entry in the chain.
        timestamp: When the event occurred.
    """

    __tablename__ = "audit_trail"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(100), nullable=False)
    event_data = Column(Text, nullable=True)  # JSON string
    hash = Column(String(64), nullable=False)
    previous_hash = Column(String(64), nullable=True, default="0" * 64)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    agent = relationship("Agent", back_populates="audit_entries")

    __table_args__ = (
        Index("idx_audit_agent", "agent_id"),
        Index("idx_audit_type", "event_type"),
        Index("idx_audit_time", "timestamp"),
    )

    @staticmethod
    def compute_hash(
        entry_id: str,
        event_type: str,
        event_data: str | None,
        previous_hash: str,
        timestamp: str,
    ) -> str:
        """Compute SHA-256 hash for a chain entry."""
        payload = f"{entry_id}:{event_type}:{event_data or ''}:{previous_hash}:{timestamp}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict:
        """Serialize audit trail entry to dictionary."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "event_type": self.event_type,
            "event_data": self.event_data,
            "hash": self.hash,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
