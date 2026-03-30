"""Pydantic schemas for Agent endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AgentCreate(BaseModel):
    """Schema for creating a new agent."""
    name: str = Field(..., min_length=1, max_length=255, description="Agent name")
    org_id: Optional[str] = Field(None, description="Organization ID")
    description: Optional[str] = Field(None, description="Agent description")
    model_type: Optional[str] = Field(None, description="AI model type (e.g. gpt-4, claude-3)")
    allowed_actions: Optional[list[str]] = Field(default_factory=list, description="Permitted actions")
    forbidden_actions: Optional[list[str]] = Field(default_factory=list, description="Forbidden actions")


class AgentUpdate(BaseModel):
    """Schema for updating an existing agent."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    model_type: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(active|paused|quarantined|decommissioned)$")
    allowed_actions: Optional[list[str]] = None
    forbidden_actions: Optional[list[str]] = None


class AgentResponse(BaseModel):
    """Schema for agent API responses."""
    id: str
    org_id: str
    name: str
    description: Optional[str] = None
    model_type: Optional[str] = None
    status: str
    allowed_actions: list[str] = []
    forbidden_actions: list[str] = []
    risk_score: float = 0.0
    health_score: float = 1.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
