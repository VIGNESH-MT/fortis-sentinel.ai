"""Pydantic schemas for Audit Trail endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AuditTrailResponse(BaseModel):
    """Schema for audit trail API responses."""
    id: str
    agent_id: str
    event_type: str
    event_data: Optional[str] = None
    hash: str
    previous_hash: Optional[str] = None
    timestamp: Optional[datetime] = None

    model_config = {"from_attributes": True}
