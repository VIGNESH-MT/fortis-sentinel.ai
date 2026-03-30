"""Pydantic schemas for Compliance endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ComplianceRunRequest(BaseModel):
    """Schema for triggering a compliance check."""
    agent_id: str = Field(..., description="Agent UUID to evaluate")
    framework: str = Field(
        ...,
        description="Regulatory framework: EU_AI_Act, Colorado_AI_Act, Singapore_MGF, ISO_42001",
    )


class ComplianceCheckResponse(BaseModel):
    """Schema for compliance check API responses."""
    id: str
    agent_id: str
    framework: str
    status: str
    score: Optional[float] = None
    findings: Optional[str] = None
    recommendations: Optional[str] = None
    checked_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
