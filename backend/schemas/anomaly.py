"""Pydantic schemas for Anomaly endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AnomalyResponse(BaseModel):
    """Schema for anomaly API responses."""
    id: str
    agent_id: str
    detected_at: Optional[datetime] = None
    anomaly_type: str
    severity: str
    confidence: float
    description: Optional[str] = None
    framework_source: Optional[str] = None
    raw_metrics: Optional[str] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
