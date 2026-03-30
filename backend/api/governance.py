"""
FORTIS SENTINEL - Governance API Router

Manage governance policies and run governance checks using the
15 mathematical frameworks.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.agent import Agent
from models.governance_config import GovernanceConfig
from models.anomaly import Anomaly
from schemas.governance import (
    GovernanceConfigCreate,
    GovernanceConfigUpdate,
    GovernanceConfigResponse,
    GovernanceCheckResult,
)
from schemas.anomaly import AnomalyResponse

router = APIRouter()


# ---------------------------------------------------------------------------
# Governance Policies CRUD
# ---------------------------------------------------------------------------

@router.get("/policies", response_model=list[GovernanceConfigResponse])
async def list_policies(
    agent_id: Optional[str] = Query(None),
    policy_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List governance policies with optional filtering."""
    query = select(GovernanceConfig)
    if agent_id:
        query = query.where(GovernanceConfig.agent_id == agent_id)
    if policy_type:
        query = query.where(GovernanceConfig.policy_type == policy_type)
    if is_active is not None:
        query = query.where(GovernanceConfig.is_active == is_active)
    query = query.order_by(GovernanceConfig.created_at.desc())
    result = await db.execute(query)
    policies = result.scalars().all()
    return [GovernanceConfigResponse.model_validate(p) for p in policies]


@router.post("/policies", response_model=GovernanceConfigResponse, status_code=201)
async def create_policy(
    payload: GovernanceConfigCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new governance policy for an agent."""
    # Verify agent exists
    agent_result = await db.execute(select(Agent).where(Agent.id == payload.agent_id))
    if not agent_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail=f"Agent {payload.agent_id} not found")

    policy = GovernanceConfig(
        id=str(uuid.uuid4()),
        agent_id=payload.agent_id,
        policy_name=payload.policy_name,
        policy_type=payload.policy_type,
        rules=payload.rules,
        enforcement_level=payload.enforcement_level,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(policy)
    await db.flush()
    await db.refresh(policy)
    return GovernanceConfigResponse.model_validate(policy)


@router.patch("/policies/{policy_id}", response_model=GovernanceConfigResponse)
async def update_policy(
    policy_id: str,
    payload: GovernanceConfigUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing governance policy."""
    result = await db.execute(select(GovernanceConfig).where(GovernanceConfig.id == policy_id))
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(policy, field, value)
    policy.updated_at = datetime.utcnow()

    await db.flush()
    await db.refresh(policy)
    return GovernanceConfigResponse.model_validate(policy)


@router.delete("/policies/{policy_id}", status_code=204)
async def delete_policy(policy_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a governance policy."""
    result = await db.execute(select(GovernanceConfig).where(GovernanceConfig.id == policy_id))
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found")
    await db.delete(policy)


# ---------------------------------------------------------------------------
# Governance Check — run all 15 engines
# ---------------------------------------------------------------------------

@router.post("/check/{agent_id}", response_model=GovernanceCheckResult)
async def run_governance_check(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Run all 15 mathematical governance engines against an agent.
    Returns an aggregated governance score and per-engine results.
    """
    # Verify agent exists
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

    # Import and run orchestrator
    from engines.orchestrator import GovernanceOrchestrator

    orchestrator = GovernanceOrchestrator()
    check_result = orchestrator.run_all(agent.to_dict())

    # Persist any anomalies detected
    for anomaly_data in check_result.get("anomalies", []):
        anomaly = Anomaly(
            id=str(uuid.uuid4()),
            agent_id=agent_id,
            detected_at=datetime.utcnow(),
            anomaly_type=anomaly_data.get("type", "unknown"),
            severity=anomaly_data.get("severity", "medium"),
            confidence=anomaly_data.get("confidence", 0.5),
            description=anomaly_data.get("description", ""),
            framework_source=anomaly_data.get("framework_source", ""),
            raw_metrics=json.dumps(anomaly_data.get("metrics", {})),
            resolved=False,
        )
        db.add(anomaly)

    # Update agent risk/health scores
    agent.risk_score = check_result.get("risk_score", agent.risk_score)
    agent.health_score = check_result.get("health_score", agent.health_score)
    agent.updated_at = datetime.utcnow()

    await db.flush()

    overall_score = check_result.get("overall_score", 0.85)
    if overall_score >= 0.8:
        status = "safe"
    elif overall_score >= 0.5:
        status = "warning"
    else:
        status = "critical"

    return GovernanceCheckResult(
        agent_id=agent_id,
        overall_score=overall_score,
        status=status,
        engine_results=check_result.get("engine_results", {}),
        anomalies_detected=len(check_result.get("anomalies", [])),
        timestamp=datetime.utcnow(),
    )


# ---------------------------------------------------------------------------
# Anomalies
# ---------------------------------------------------------------------------

@router.get("/anomalies", response_model=list[AnomalyResponse])
async def list_anomalies(
    agent_id: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    resolved: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List detected anomalies with filtering."""
    query = select(Anomaly).offset(skip).limit(limit)
    if agent_id:
        query = query.where(Anomaly.agent_id == agent_id)
    if severity:
        query = query.where(Anomaly.severity == severity)
    if resolved is not None:
        query = query.where(Anomaly.resolved == resolved)
    query = query.order_by(Anomaly.detected_at.desc())
    result = await db.execute(query)
    anomalies = result.scalars().all()
    return [AnomalyResponse.model_validate(a) for a in anomalies]


@router.post("/anomalies/{anomaly_id}/resolve", response_model=AnomalyResponse)
async def resolve_anomaly(anomaly_id: str, db: AsyncSession = Depends(get_db)):
    """Mark an anomaly as resolved."""
    result = await db.execute(select(Anomaly).where(Anomaly.id == anomaly_id))
    anomaly = result.scalar_one_or_none()
    if not anomaly:
        raise HTTPException(status_code=404, detail=f"Anomaly {anomaly_id} not found")
    anomaly.resolved = True
    anomaly.resolved_at = datetime.utcnow()
    await db.flush()
    await db.refresh(anomaly)
    return AnomalyResponse.model_validate(anomaly)
