"""
FORTIS SENTINEL - Execution Logs API Router

Query and create execution logs for agent actions.
Provides filtering by agent, time range, and status.
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
from models.execution_log import ExecutionLog
from schemas.execution_log import LogCreate, LogResponse

router = APIRouter()


@router.get("/", response_model=list[LogResponse])
async def list_logs(
    agent_id: Optional[str] = Query(None, description="Filter by agent"),
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """List execution logs with optional filtering."""
    query = select(ExecutionLog).offset(skip).limit(limit)
    if agent_id:
        query = query.where(ExecutionLog.agent_id == agent_id)
    if status:
        query = query.where(ExecutionLog.status == status)
    query = query.order_by(ExecutionLog.timestamp.desc())
    result = await db.execute(query)
    logs = result.scalars().all()
    return [LogResponse.model_validate(log) for log in logs]


@router.post("/", response_model=LogResponse, status_code=201)
async def create_log(
    payload: LogCreate,
    db: AsyncSession = Depends(get_db),
):
    """Record a new execution log entry."""
    # Verify agent exists
    agent_result = await db.execute(select(Agent).where(Agent.id == payload.agent_id))
    if not agent_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail=f"Agent {payload.agent_id} not found")

    log = ExecutionLog(
        id=str(uuid.uuid4()),
        agent_id=payload.agent_id,
        action=payload.action,
        resource_accessed=payload.resource_accessed,
        status=payload.status,
        result=payload.result,
        duration_ms=payload.duration_ms,
        timestamp=datetime.utcnow(),
        created_at=datetime.utcnow(),
    )
    db.add(log)
    await db.flush()
    await db.refresh(log)
    return LogResponse.model_validate(log)


@router.get("/stats")
async def log_stats(
    agent_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get execution log statistics."""
    query = select(ExecutionLog.status, func.count(ExecutionLog.id)).group_by(ExecutionLog.status)
    if agent_id:
        query = query.where(ExecutionLog.agent_id == agent_id)
    result = await db.execute(query)
    stats = {row[0] or "unknown": row[1] for row in result.all()}
    return {"total": sum(stats.values()), "by_status": stats}


@router.get("/{log_id}", response_model=LogResponse)
async def get_log(log_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve a specific execution log entry."""
    result = await db.execute(select(ExecutionLog).where(ExecutionLog.id == log_id))
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail=f"Log {log_id} not found")
    return LogResponse.model_validate(log)
