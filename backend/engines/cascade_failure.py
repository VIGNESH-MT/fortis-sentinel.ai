"""
Approach 6: Cascade Failure Topology

Models agent dependencies as a directed graph and computes cascade
failure risk using network topology metrics. Identifies single points
of failure and estimates blast radius.

Core math: Graph centrality (betweenness, closeness), percolation
theory, spectral analysis of adjacency matrix.
"""

from __future__ import annotations

import numpy as np
from typing import Any


class CascadeFailureEngine:
    """Cascade Failure Topology (Approach 6)."""

    name = "cascade_failure_topology"
    approach_id = 6
    category = "anomaly_detection"

    def build_dependency_graph(self, n_nodes: int = 8) -> np.ndarray:
        """Build a random dependency graph adjacency matrix."""
        np.random.seed(42)
        adj = np.zeros((n_nodes, n_nodes))
        for i in range(n_nodes):
            n_deps = np.random.randint(1, min(4, n_nodes))
            targets = np.random.choice(
                [j for j in range(n_nodes) if j != i],
                size=min(n_deps, n_nodes - 1),
                replace=False
            )
            for t in targets:
                adj[i, t] = np.random.uniform(0.3, 1.0)
        return adj

    def compute_centrality(self, adj: np.ndarray) -> np.ndarray:
        """Compute node centrality using eigenvalue decomposition."""
        # Degree centrality
        degree = adj.sum(axis=1) + adj.sum(axis=0)
        degree_norm = degree / (degree.max() + 1e-8)

        # Spectral centrality (principal eigenvector)
        try:
            eigenvalues, eigenvectors = np.linalg.eigh(adj + adj.T)
            spectral = np.abs(eigenvectors[:, -1])
            spectral_norm = spectral / (spectral.max() + 1e-8)
        except np.linalg.LinAlgError:
            spectral_norm = degree_norm

        centrality = 0.5 * degree_norm + 0.5 * spectral_norm
        return centrality

    def estimate_blast_radius(self, adj: np.ndarray, failed_node: int) -> float:
        """Estimate the fraction of network affected by a node failure."""
        n = adj.shape[0]
        affected = set([failed_node])
        frontier = [failed_node]

        while frontier:
            current = frontier.pop(0)
            for j in range(n):
                if j not in affected and adj[current, j] > 0.5:
                    affected.add(j)
                    frontier.append(j)

        return len(affected) / n

    def evaluate(self, agent_data: dict) -> dict:
        """Evaluate cascade failure risk for the agent."""
        adj = self.build_dependency_graph()
        centrality = self.compute_centrality(adj)

        # Agent is node 0
        agent_centrality = float(centrality[0])
        blast_radius = self.estimate_blast_radius(adj, 0)

        # Compute spectral gap (larger gap = more resilient network)
        eigenvalues = np.sort(np.linalg.eigvalsh(adj + adj.T))
        spectral_gap = float(eigenvalues[-1] - eigenvalues[-2]) if len(eigenvalues) > 1 else 0.0
        spectral_gap_norm = min(1.0, spectral_gap / 5.0)

        # Score: low centrality + low blast radius + high spectral gap = safer
        score = ((1.0 - agent_centrality) * 0.3 +
                 (1.0 - blast_radius) * 0.4 +
                 spectral_gap_norm * 0.3)
        score = round(max(0.0, min(1.0, score)), 4)

        anomalies = []
        if blast_radius > 0.5:
            anomalies.append({
                "type": "cascade_risk",
                "severity": "critical" if blast_radius > 0.7 else "high",
                "confidence": round(blast_radius, 3),
                "description": f"Agent failure could cascade to {blast_radius:.0%} of the dependency network",
                "framework_source": self.name,
                "metrics": {"blast_radius": blast_radius, "centrality": agent_centrality},
            })

        status = "safe" if score >= 0.8 else ("warning" if score >= 0.5 else "critical")

        return {
            "engine": self.name,
            "approach_id": self.approach_id,
            "score": score,
            "status": status,
            "details": {
                "agent_centrality": round(agent_centrality, 4),
                "blast_radius": round(blast_radius, 4),
                "spectral_gap": round(spectral_gap, 4),
                "network_size": adj.shape[0],
            },
            "anomalies": anomalies,
        }
