"""
FORTIS SENTINEL - Governance Orchestrator

Runs all 15 mathematical governance engines and aggregates results
into a unified governance score with per-engine breakdown.
"""

from __future__ import annotations
from datetime import datetime
from typing import Any

from engines.action_space_geometry import ActionSpaceGeometryEngine
from engines.causal_liability import CausalLiabilityEngine
from engines.reversibility import ReversibilityEngine
from engines.anomaly_detection import AnomalyDetectionEngine
from engines.behavioral_contracts import BehavioralContractEngine
from engines.cascade_failure import CascadeFailureEngine
from engines.semantic_boundary import SemanticBoundaryEngine
from engines.intent_alignment import IntentAlignmentEngine
from engines.goal_hijacking import GoalHijackingEngine
from engines.game_theory import GameTheoryEngine
from engines.deadlock_scheduling import DeadlockSchedulingEngine
from engines.optimal_transport import OptimalTransportEngine
from engines.crypto_audit import CryptoAuditEngine
from engines.causal_responsibility import CausalResponsibilityEngine
from engines.formal_compliance import FormalComplianceEngine


class GovernanceOrchestrator:
    """Orchestrates all 15 governance engines and aggregates results."""

    # Engine weights by category
    CATEGORY_WEIGHTS = {
        "safety": 0.30,
        "anomaly_detection": 0.20,
        "orchestration": 0.15,
        "compliance": 0.20,
        "liability": 0.15,
    }

    def __init__(self):
        self.engines = [
            ActionSpaceGeometryEngine(),
            CausalLiabilityEngine(),
            ReversibilityEngine(),
            AnomalyDetectionEngine(),
            BehavioralContractEngine(),
            CascadeFailureEngine(),
            SemanticBoundaryEngine(),
            IntentAlignmentEngine(),
            GoalHijackingEngine(),
            GameTheoryEngine(),
            DeadlockSchedulingEngine(),
            OptimalTransportEngine(),
            CryptoAuditEngine(),
            CausalResponsibilityEngine(),
            FormalComplianceEngine(),
        ]

    def run_all(self, agent_data: dict) -> dict:
        """Run all engines and return aggregated results."""
        engine_results = {}
        all_anomalies = []
        category_scores = {}

        for engine in self.engines:
            try:
                result = engine.evaluate(agent_data)
                engine_results[engine.name] = result

                # Collect anomalies
                for anomaly in result.get("anomalies", []):
                    all_anomalies.append(anomaly)

                # Group by category
                cat = engine.category
                if cat not in category_scores:
                    category_scores[cat] = []
                category_scores[cat].append(result.get("score", 0.5))

            except Exception as e:
                engine_results[engine.name] = {
                    "engine": engine.name,
                    "approach_id": engine.approach_id,
                    "score": 0.5,
                    "status": "error",
                    "details": {"error": str(e)},
                    "anomalies": [],
                }

        # Compute weighted overall score
        overall = 0.0
        for cat, weight in self.CATEGORY_WEIGHTS.items():
            if cat in category_scores:
                cat_avg = sum(category_scores[cat]) / len(category_scores[cat])
                overall += cat_avg * weight

        overall = round(max(0.0, min(1.0, overall)), 4)

        # Compute risk and health from results
        risk_score = round(max(0.0, min(1.0, 1.0 - overall)), 4)
        health_score = overall

        return {
            "overall_score": overall,
            "risk_score": risk_score,
            "health_score": health_score,
            "engine_results": engine_results,
            "category_scores": {k: round(sum(v)/len(v), 4) for k, v in category_scores.items()},
            "anomalies": all_anomalies,
            "engines_run": len(self.engines),
            "timestamp": datetime.utcnow().isoformat(),
        }
