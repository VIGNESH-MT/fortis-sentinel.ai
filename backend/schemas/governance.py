"""Pydantic schemas for Governance endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class GovernanceConfigCreate(BaseModel):
    """Schema for creating a governance policy."""
    agent_id: str = Field(..., description="Agent UUID")
    policy_name: str = Field(..., min_length=1, max_length=255, description="Policy name")
    policy_type: str = Field(
        default="safety",
        pattern="^(safety|compliance|operational|ethical)$",
        description="Policy category",
    )
    rules: Optional[str] = Field(None, description="JSON rules definition")
    enforcement_level: str = Field(
        default="warning",
        pattern="^(advisory|warning|blocking)$",
        description="Enforcement level",
    )


class GovernanceConfigUpdate(BaseModel):
    """Schema for updating a governance policy."""
    policy_name: Optional[str] = Field(None, min_length=1, max_length=255)
    policy_type: Optional[str] = Field(None, pattern="^(safety|compliance|operational|ethical)$")
    rules: Optional[str] = None
    enforcement_level: Optional[str] = Field(None, pattern="^(advisory|warning|blocking)$")
    is_active: Optional[bool] = None


class GovernanceConfigResponse(BaseModel):
    """Schema for governance config API responses."""
    id: str
    agent_id: str
    policy_name: str
    policy_type: str
    rules: Optional[str] = None
    enforcement_level: str
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class GovernanceCheckResult(BaseModel):
    """Result of running all governance engines on an agent."""
    agent_id: str
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Aggregate governance score")
    status: str = Field(..., description="safe, warning, or critical")
    engine_results: dict = Field(default_factory=dict, description="Per-engine results")
    anomalies_detected: int = 0
    timestamp: datetime
