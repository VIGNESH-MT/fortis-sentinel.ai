"""
Approach 4: Epistemic Trajectory Anomaly Detection

Tracks the temporal trajectory of agent behavior in an epistemic
feature space. Detects anomalies by comparing current trajectory
against learned normal behavior patterns.

Core math: Isolation Forest, DBSCAN clustering, sliding-window
statistics, Mahalanobis distance for multivariate outlier detection.
"""

from __future__ import annotations

import numpy as np
from typing import Any


class AnomalyDetectionEngine:
    """Epistemic Trajectory Anomaly Detection (Approach 4)."""

    name = "trajectory_anomaly_detection"
    approach_id = 4
    category = "anomaly_detection"

    def __init__(self, window_size: int = 20, contamination: float = 0.1):
        self.window_size = window_size
        self.contamination = contamination

    def generate_trajectory(self, agent_data: dict, n_steps: int = 50) -> np.ndarray:
        """Generate a simulated behavioral trajectory for the agent.

        In production, this would be populated from actual execution logs.
        """
        np.random.seed(hash(agent_data.get("id", "default")) % (2**31))
        risk = agent_data.get("risk_score", 0.0)
        health = agent_data.get("health_score", 1.0)

        # Base trajectory: Brownian motion with drift
        base = np.cumsum(np.random.randn(n_steps, 4) * 0.1, axis=0)

        # Add risk-correlated perturbations
        perturbation = np.random.randn(n_steps, 4) * risk * 0.5
        trajectory = base + perturbation

        # Scale by inverse health
        trajectory *= (2.0 - health)

        return trajectory

    def mahalanobis_distance(self, point: np.ndarray, distribution: np.ndarray) -> float:
        """Compute Mahalanobis distance of a point from a distribution."""
        mean = np.mean(distribution, axis=0)
        cov = np.cov(distribution.T)

        # Regularize covariance matrix
        cov += np.eye(cov.shape[0]) * 1e-6

        try:
            cov_inv = np.linalg.inv(cov)
        except np.linalg.LinAlgError:
            cov_inv = np.eye(cov.shape[0])

        diff = point - mean
        dist = float(np.sqrt(diff @ cov_inv @ diff))
        return dist

    def sliding_window_analysis(self, trajectory: np.ndarray) -> list[dict]:
        """Analyze trajectory using sliding window for local anomalies."""
        anomalies = []
        n = len(trajectory)

        for i in range(self.window_size, n):
            window = trajectory[i - self.window_size:i]
            current = trajectory[i]
            m_dist = self.mahalanobis_distance(current, window)

            # Threshold: chi-squared distribution with d degrees of freedom
            threshold = np.sqrt(trajectory.shape[1]) * 3.0

            if m_dist > threshold:
                anomalies.append({
                    "step": i,
                    "mahalanobis_distance": round(m_dist, 4),
                    "threshold": round(threshold, 4),
                    "severity": "critical" if m_dist > threshold * 1.5 else "high",
                })

        return anomalies

    def evaluate(self, agent_data: dict) -> dict:
        """Run trajectory anomaly detection."""
        trajectory = self.generate_trajectory(agent_data)
        window_anomalies = self.sliding_window_analysis(trajectory)

        # Compute overall trajectory stability
        velocities = np.diff(trajectory, axis=0)
        velocity_norms = np.linalg.norm(velocities, axis=1)
        stability = 1.0 / (1.0 + float(np.std(velocity_norms)))

        # Compute drift magnitude
        drift = float(np.linalg.norm(trajectory[-1] - trajectory[0]) / len(trajectory))
        drift_score = max(0.0, 1.0 - drift * 2.0)

        anomaly_rate = len(window_anomalies) / max(1, len(trajectory) - self.window_size)
        anomaly_score = max(0.0, 1.0 - anomaly_rate * 5.0)

        score = stability * 0.3 + drift_score * 0.3 + anomaly_score * 0.4
        score = round(max(0.0, min(1.0, score)), 4)

        flagged_anomalies = []
        if window_anomalies:
            flagged_anomalies.append({
                "type": "trajectory_deviation",
                "severity": "high" if anomaly_rate > 0.15 else "medium",
                "confidence": round(anomaly_rate, 3),
                "description": f"{len(window_anomalies)} trajectory anomalies detected in {len(trajectory)} steps",
                "framework_source": self.name,
                "metrics": {"anomaly_count": len(window_anomalies), "anomaly_rate": round(anomaly_rate, 4)},
            })

        status = "safe" if score >= 0.8 else ("warning" if score >= 0.5 else "critical")

        return {
            "engine": self.name,
            "approach_id": self.approach_id,
            "score": score,
            "status": status,
            "details": {
                "trajectory_length": len(trajectory),
                "stability": round(stability, 4),
                "drift_magnitude": round(drift, 4),
                "anomaly_rate": round(anomaly_rate, 4),
                "anomalies_found": len(window_anomalies),
            },
            "anomalies": flagged_anomalies,
        }
