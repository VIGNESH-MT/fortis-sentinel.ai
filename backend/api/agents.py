"""
FORTIS SENTINEL - Agents API Router

Full CRUD for AI agent registration and management.
Supports listing, creation, retrieval, update, deletion, and quarantine.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.agent import Agent
from schemas.agent import AgentCreate, AgentUpdate, AgentResponse

router = APIRouter()


@router.get("/", response_model=list[AgentResponse])
async def list_agents(
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List all registered agents with optional filtering."""
    query = select(Agent).offset(skip).limit(limit)
    if status:
        query = query.where(Agent.status == status)
    query = query.order_by(Agent.created_at.desc())
    result = await db.execute(query)
    agents = result.scalars().all()
    return [AgentResponse.model_validate(a) for a in agents]


@router.get("/count")
async def count_agents(db: AsyncSession = Depends(get_db)):
    """Get total agent count by status."""
    result = await db.execute(
        select(Agent.status, func.count(Agent.id)).group_by(Agent.status)
    )
    counts = {row[0]: row[1] for row in result.all()}
    total = sum(counts.values())
    return {"total": total, "by_status": counts}


@router.post("/", response_model=AgentResponse, status_code=201)
async def create_agent(
    payload: AgentCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new AI agent with the governance platform."""
    agent = Agent(
        id=str(uuid.uuid4()),
        org_id=payload.org_id or str(uuid.uuid4()),
        name=payload.name,
        description=payload.description,
        model_type=payload.model_type,
        allowed_actions=payload.allowed_actions or [],
        forbidden_actions=payload.forbidden_actions or [],
        status="active",
        risk_score=0.0,
        health_score=1.0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(agent)
    await db.flush()
    await db.refresh(agent)
    return AgentResponse.model_validate(agent)


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve a specific agent by ID."""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    return AgentResponse.model_validate(agent)


@router.patch("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    payload: AgentUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing agent."""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)
    agent.updated_at = datetime.utcnow()

    await db.flush()
    await db.refresh(agent)
    return AgentResponse.model_validate(agent)


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Remove an agent and all associated data."""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    await db.delete(agent)


@router.post("/{agent_id}/quarantine", response_model=AgentResponse)
async def quarantine_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Quarantine an agent — immediately halt all operations."""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    agent.status = "quarantined"
    agent.updated_at = datetime.utcnow()
    await db.flush()
    await db.refresh(agent)
    return AgentResponse.model_validate(agent)


@router.post("/{agent_id}/activate", response_model=AgentResponse)
async def activate_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Re-activate a paused or quarantined agent."""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    if agent.status == "decommissioned":
        raise HTTPException(status_code=400, detail="Cannot reactivate a decommissioned agent")
    agent.status = "active"
    agent.updated_at = datetime.utcnow()
    await db.flush()
    await db.refresh(agent)
    return AgentResponse.model_validate(agent)
