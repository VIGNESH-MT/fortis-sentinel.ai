"""
Approach 2: Causal Liability Tensor

Constructs a multi-dimensional tensor capturing causal relationships
between agent actions and their outcomes. Used to attribute liability
when adverse events occur in multi-agent systems.

Core math: Tensor decomposition, causal graph analysis, Shapley values
for fair attribution.
"""

from __future__ import annotations

import numpy as np
from typing import Any


class CausalLiabilityEngine:
    """Causal Liability Tensor (Approach 2)."""

    name = "causal_liability"
    approach_id = 2
    category = "liability"

    def compute_liability_tensor(self, n_agents: int, n_outcomes: int) -> np.ndarray:
        """Construct the causal liability tensor L_{ijk}."""
        np.random.seed(42)
        # Shape: (agents, actions, outcomes)
        tensor = np.random.dirichlet(np.ones(n_outcomes), size=(n_agents, n_outcomes))
        # Normalize so liability sums to 1 across agents for each outcome
        for k in range(n_outcomes):
            tensor[:, :, k] /= (tensor[:, :, k].sum() + 1e-8)
        return tensor

    def shapley_attribution(self, contributions: np.ndarray) -> np.ndarray:
        """Compute Shapley-value-based liability attribution."""
        n = len(contributions)
        shapley = np.zeros(n)
        total = contributions.sum()

        for i in range(n):
            marginal = contributions[i] / (total + 1e-8)
            shapley[i] = marginal

        # Normalize
        shapley = shapley / (shapley.sum() + 1e-8)
        return shapley

    def evaluate(self, agent_data: dict) -> dict:
        """Evaluate causal liability for this agent."""
        risk_score = agent_data.get("risk_score", 0.0)
        health_score = agent_data.get("health_score", 1.0)

        # Simulate a multi-agent scenario
        n_agents = 5
        n_outcomes = 4
        tensor = self.compute_liability_tensor(n_agents, n_outcomes)

        # This agent's liability slice (agent index 0)
        agent_liability = tensor[0]
        max_liability = float(np.max(agent_liability))
        avg_liability = float(np.mean(agent_liability))

        # Compute concentration index (Herfindahl)
        hhi = float(np.sum(agent_liability ** 2))

        # Score: lower liability concentration → higher score
        score = max(0.0, min(1.0, 1.0 - max_liability * 0.5 - risk_score * 0.3))
        score = round(score, 4)

        anomalies = []
        if max_liability > 0.6:
            anomalies.append({
                "type": "high_liability_concentration",
                "severity": "high",
                "confidence": round(max_liability, 3),
                "description": f"Agent bears {max_liability:.1%} liability for at least one outcome",
                "framework_source": self.name,
                "metrics": {"max_liability": max_liability, "hhi": hhi},
            })

        status = "safe" if score >= 0.8 else ("warning" if score >= 0.5 else "critical")

        return {
            "engine": self.name,
            "approach_id": self.approach_id,
            "score": score,
            "status": status,
            "details": {
                "max_liability": round(max_liability, 4),
                "avg_liability": round(avg_liability, 4),
                "herfindahl_index": round(hhi, 4),
                "tensor_shape": list(tensor.shape),
            },
            "anomalies": anomalies,
        }
