"""Pydantic schemas for Execution Log endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LogCreate(BaseModel):
    """Schema for creating an execution log entry."""
    agent_id: str = Field(..., description="Agent UUID")
    action: str = Field(..., min_length=1, max_length=255, description="Action performed")
    resource_accessed: Optional[str] = Field(None, description="Resource accessed")
    status: Optional[str] = Field(None, description="Outcome status")
    result: Optional[str] = Field(None, description="Result or error message")
    duration_ms: Optional[int] = Field(None, ge=0, description="Duration in ms")


class LogResponse(BaseModel):
    """Schema for execution log API responses."""
    id: str
    agent_id: str
    timestamp: Optional[datetime] = None
    action: str
    resource_accessed: Optional[str] = None
    status: Optional[str] = None
    result: Optional[str] = None
    duration_ms: Optional[int] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
