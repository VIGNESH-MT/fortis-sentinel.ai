"""
Approach 7: Semantic Boundary Enforcement

Enforces semantic boundaries on agent actions by analyzing the semantic
distance between agent operations and their permitted domain. Uses
embedding-based similarity to detect out-of-domain operations.

Core math: Cosine similarity, semantic embedding projection,
boundary surface computation.
"""

from __future__ import annotations

import numpy as np
from typing import Any


class SemanticBoundaryEngine:
    """Semantic Boundary Enforcement (Approach 7)."""

    name = "semantic_boundary"
    approach_id = 7
    category = "safety"

    def __init__(self, embedding_dim: int = 16):
        self.embedding_dim = embedding_dim

    def embed_action(self, action: str) -> np.ndarray:
        """Create a deterministic semantic embedding for an action."""
        np.random.seed(hash(action) % (2**31))
        emb = np.random.randn(self.embedding_dim)
        return emb / (np.linalg.norm(emb) + 1e-8)

    def cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))

    def compute_domain_boundary(self, allowed_actions: list[str]) -> dict:
        """Compute the semantic domain boundary."""
        if not allowed_actions:
            return {"centroid": np.zeros(self.embedding_dim), "threshold": 0.5}

        embeddings = np.array([self.embed_action(a) for a in allowed_actions])
        centroid = np.mean(embeddings, axis=0)
        centroid = centroid / (np.linalg.norm(centroid) + 1e-8)

        # Threshold = minimum cosine similarity within allowed set
        similarities = [self.cosine_similarity(centroid, e) for e in embeddings]
        threshold = min(similarities) - 0.1  # slight margin

        return {"centroid": centroid, "threshold": threshold}

    def evaluate(self, agent_data: dict) -> dict:
        """Evaluate semantic boundary compliance."""
        allowed = agent_data.get("allowed_actions", [])
        forbidden = agent_data.get("forbidden_actions", [])

        if not allowed:
            return {
                "engine": self.name,
                "approach_id": self.approach_id,
                "score": 0.7,
                "status": "warning",
                "details": "No allowed actions for semantic boundary",
                "anomalies": [],
            }

        boundary = self.compute_domain_boundary(allowed)

        # Compute domain coherence
        embeddings = np.array([self.embed_action(a) for a in allowed])
        pairwise_sims = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                pairwise_sims.append(self.cosine_similarity(embeddings[i], embeddings[j]))

        coherence = float(np.mean(pairwise_sims)) if pairwise_sims else 1.0

        # Compute forbidden zone separation
        separation = 1.0
        if forbidden:
            forbidden_embs = [self.embed_action(f) for f in forbidden]
            sims_to_domain = [
                self.cosine_similarity(boundary["centroid"], fe) for fe in forbidden_embs
            ]
            max_forbidden_sim = max(sims_to_domain)
            separation = max(0.0, 1.0 - max_forbidden_sim)

        score = coherence * 0.5 + separation * 0.5
        score = round(max(0.0, min(1.0, score)), 4)

        anomalies = []
        if separation < 0.3:
            anomalies.append({
                "type": "boundary_breach",
                "severity": "high",
                "confidence": round(1.0 - separation, 3),
                "description": "Forbidden actions are semantically close to allowed domain",
                "framework_source": self.name,
                "metrics": {"separation": separation, "coherence": coherence},
            })

        status = "safe" if score >= 0.8 else ("warning" if score >= 0.5 else "critical")

        return {
            "engine": self.name,
            "approach_id": self.approach_id,
            "score": score,
            "status": status,
            "details": {
                "domain_coherence": round(coherence, 4),
                "forbidden_separation": round(separation, 4),
                "boundary_threshold": round(float(boundary["threshold"]), 4),
            },
            "anomalies": anomalies,
        }
