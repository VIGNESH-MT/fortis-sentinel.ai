"""
FORTIS SENTINEL - Compliance API Router

Run compliance evaluations against regulatory frameworks and retrieve results.
Supports EU AI Act, Colorado AI Act, Singapore MGF, and ISO 42001.
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
from models.compliance_check import ComplianceCheck
from models.audit_trail import AuditTrail
from schemas.compliance import ComplianceRunRequest, ComplianceCheckResponse
from schemas.audit import AuditTrailResponse

router = APIRouter()


# ---------------------------------------------------------------------------
# Supported frameworks and their rule sets
# ---------------------------------------------------------------------------

FRAMEWORKS = {
    "EU_AI_Act": {
        "name": "EU AI Act",
        "checks": [
            {"rule": "transparency", "description": "Agent must declare its AI nature", "weight": 0.2},
            {"rule": "human_oversight", "description": "Human-in-the-loop for high-risk decisions", "weight": 0.25},
            {"rule": "data_governance", "description": "Training data quality and bias controls", "weight": 0.2},
            {"rule": "risk_management", "description": "Documented risk management system", "weight": 0.2},
            {"rule": "record_keeping", "description": "Complete audit logs maintained", "weight": 0.15},
        ],
    },
    "Colorado_AI_Act": {
        "name": "Colorado AI Act (SB 24-205)",
        "checks": [
            {"rule": "impact_assessment", "description": "Algorithmic impact assessment completed", "weight": 0.3},
            {"rule": "consumer_notification", "description": "Consumers notified of AI interaction", "weight": 0.25},
            {"rule": "discrimination_testing", "description": "Tested for discriminatory outcomes", "weight": 0.25},
            {"rule": "developer_duty", "description": "Developer duty of care documented", "weight": 0.2},
        ],
    },
    "Singapore_MGF": {
        "name": "Singapore Model AI Governance Framework",
        "checks": [
            {"rule": "accountability", "description": "Clear accountability structure", "weight": 0.25},
            {"rule": "explainability", "description": "Decision explainability mechanisms", "weight": 0.25},
            {"rule": "fairness", "description": "Fairness and non-discrimination", "weight": 0.25},
            {"rule": "safety_resilience", "description": "Safety and resilience measures", "weight": 0.25},
        ],
    },
    "ISO_42001": {
        "name": "ISO/IEC 42001 AI Management System",
        "checks": [
            {"rule": "ai_policy", "description": "AI management policy defined", "weight": 0.2},
            {"rule": "risk_assessment", "description": "AI risk assessment conducted", "weight": 0.2},
            {"rule": "performance_monitoring", "description": "Performance metrics tracked", "weight": 0.2},
            {"rule": "continual_improvement", "description": "Improvement processes documented", "weight": 0.2},
            {"rule": "competence", "description": "Staff competence for AI oversight", "weight": 0.2},
        ],
    },
}


def _evaluate_compliance(agent_data: dict, framework_key: str) -> dict:
    """Evaluate an agent against a regulatory framework.

    Uses agent properties (allowed/forbidden actions, governance configs,
    risk score, etc.) to simulate compliance scoring.
    """
    framework = FRAMEWORKS[framework_key]
    findings = []
    total_score = 0.0

    for check in framework["checks"]:
        # Heuristic scoring based on agent configuration
        rule_score = 0.0

        # Agents with lower risk scores tend to be more compliant
        risk_factor = 1.0 - (agent_data.get("risk_score", 0.0) * 0.3)

        # Agents with explicit action constraints score higher
        has_constraints = bool(agent_data.get("allowed_actions")) or bool(agent_data.get("forbidden_actions"))
        constraint_factor = 0.9 if has_constraints else 0.6

        # Active agents with health > 0.7 score higher
        health_factor = min(1.0, agent_data.get("health_score", 0.5) * 1.2)

        rule_score = (risk_factor * 0.4 + constraint_factor * 0.3 + health_factor * 0.3) * 100

        status = "pass" if rule_score >= 70 else ("partial" if rule_score >= 40 else "fail")

        findings.append({
            "rule": check["rule"],
            "description": check["description"],
            "score": round(rule_score, 1),
            "status": status,
            "weight": check["weight"],
        })

        total_score += rule_score * check["weight"]

    overall_score = round(total_score, 1)
    if overall_score >= 80:
        overall_status = "compliant"
    elif overall_score >= 50:
        overall_status = "partial"
    else:
        overall_status = "non_compliant"

    recommendations = []
    for f in findings:
        if f["status"] != "pass":
            recommendations.append(f"Improve {f['rule']}: {f['description']}")

    return {
        "score": overall_score,
        "status": overall_status,
        "findings": findings,
        "recommendations": recommendations,
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/frameworks")
async def list_frameworks():
    """List all supported regulatory frameworks."""
    return {
        key: {"name": fw["name"], "checks_count": len(fw["checks"])}
        for key, fw in FRAMEWORKS.items()
    }


@router.post("/run", response_model=ComplianceCheckResponse, status_code=201)
async def run_compliance_check(
    payload: ComplianceRunRequest,
    db: AsyncSession = Depends(get_db),
):
    """Run a compliance evaluation against a regulatory framework."""
    if payload.framework not in FRAMEWORKS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported framework: {payload.framework}. "
                   f"Supported: {list(FRAMEWORKS.keys())}",
        )

    # Verify agent exists
    result = await db.execute(select(Agent).where(Agent.id == payload.agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {payload.agent_id} not found")

    # Run evaluation
    eval_result = _evaluate_compliance(agent.to_dict(), payload.framework)

    # Persist result
    check = ComplianceCheck(
        id=str(uuid.uuid4()),
        agent_id=payload.agent_id,
        framework=payload.framework,
        status=eval_result["status"],
        score=eval_result["score"],
        findings=json.dumps(eval_result["findings"]),
        recommendations=json.dumps(eval_result["recommendations"]),
        checked_at=datetime.utcnow(),
    )
    db.add(check)

    # Add audit trail entry
    audit_id = str(uuid.uuid4())
    now_str = datetime.utcnow().isoformat()
    event_data = json.dumps({
        "framework": payload.framework,
        "score": eval_result["score"],
        "status": eval_result["status"],
    })

    # Get last audit hash
    last_audit = await db.execute(
        select(AuditTrail)
        .where(AuditTrail.agent_id == payload.agent_id)
        .order_by(AuditTrail.timestamp.desc())
        .limit(1)
    )
    last_entry = last_audit.scalar_one_or_none()
    prev_hash = last_entry.hash if last_entry else "0" * 64

    audit_hash = AuditTrail.compute_hash(audit_id, "compliance_check", event_data, prev_hash, now_str)
    audit = AuditTrail(
        id=audit_id,
        agent_id=payload.agent_id,
        event_type="compliance_check",
        event_data=event_data,
        hash=audit_hash,
        previous_hash=prev_hash,
        timestamp=datetime.utcnow(),
    )
    db.add(audit)

    await db.flush()
    await db.refresh(check)
    return ComplianceCheckResponse.model_validate(check)


@router.get("/results", response_model=list[ComplianceCheckResponse])
async def list_compliance_results(
    agent_id: Optional[str] = Query(None),
    framework: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List compliance check results with filtering."""
    query = select(ComplianceCheck).offset(skip).limit(limit)
    if agent_id:
        query = query.where(ComplianceCheck.agent_id == agent_id)
    if framework:
        query = query.where(ComplianceCheck.framework == framework)
    if status:
        query = query.where(ComplianceCheck.status == status)
    query = query.order_by(ComplianceCheck.checked_at.desc())
    result = await db.execute(query)
    checks = result.scalars().all()
    return [ComplianceCheckResponse.model_validate(c) for c in checks]


@router.get("/results/{check_id}", response_model=ComplianceCheckResponse)
async def get_compliance_result(check_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve a specific compliance check result."""
    result = await db.execute(select(ComplianceCheck).where(ComplianceCheck.id == check_id))
    check = result.scalar_one_or_none()
    if not check:
        raise HTTPException(status_code=404, detail=f"Compliance check {check_id} not found")
    return ComplianceCheckResponse.model_validate(check)


# ---------------------------------------------------------------------------
# Audit Trail
# ---------------------------------------------------------------------------

@router.get("/audit-trail", response_model=list[AuditTrailResponse])
async def list_audit_trail(
    agent_id: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """List audit trail entries with hash chain verification."""
    query = select(AuditTrail).offset(skip).limit(limit)
    if agent_id:
        query = query.where(AuditTrail.agent_id == agent_id)
    if event_type:
        query = query.where(AuditTrail.event_type == event_type)
    query = query.order_by(AuditTrail.timestamp.desc())
    result = await db.execute(query)
    entries = result.scalars().all()
    return [AuditTrailResponse.model_validate(e) for e in entries]


@router.get("/audit-trail/verify/{agent_id}")
async def verify_audit_chain(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Verify the integrity of an agent's audit trail hash chain."""
    result = await db.execute(
        select(AuditTrail)
        .where(AuditTrail.agent_id == agent_id)
        .order_by(AuditTrail.timestamp.asc())
    )
    entries = result.scalars().all()

    if not entries:
        return {"agent_id": agent_id, "chain_length": 0, "valid": True, "message": "No audit entries"}

    is_valid = True
    broken_at = None

    for i, entry in enumerate(entries):
        expected_hash = AuditTrail.compute_hash(
            entry.id,
            entry.event_type,
            entry.event_data,
            entry.previous_hash,
            entry.timestamp.isoformat() if entry.timestamp else "",
        )
        if entry.hash != expected_hash:
            is_valid = False
            broken_at = entry.id
            break

        if i > 0 and entry.previous_hash != entries[i - 1].hash:
            is_valid = False
            broken_at = entry.id
            break

    return {
        "agent_id": agent_id,
        "chain_length": len(entries),
        "valid": is_valid,
        "broken_at": broken_at,
        "message": "Chain integrity verified" if is_valid else f"Chain broken at entry {broken_at}",
    }
