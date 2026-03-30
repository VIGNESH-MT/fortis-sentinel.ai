# 🛡️ FORTIS SENTINEL v0.1.0

**Enterprise-Grade Agentic AI Governance & Verification Platform**

FORTIS SENTINEL is a production-grade platform for governing autonomous AI agents. It uses **15 proprietary mathematical frameworks** to guarantee agent safety, compliance, and reliability across multi-agent systems.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (React 18)                  │
│  Dashboard · Agents · Governance · Compliance · Audit   │
├─────────────────────────────────────────────────────────┤
│                    FastAPI Backend                        │
│  REST API · WebSocket · Async SQLAlchemy                │
├──────────┬──────────┬───────────┬──────────────────────┤
│ 15 Math  │  Policy  │ Compliance│  Crypto Audit        │
│ Engines  │  Engine  │  Engine   │  (Merkle Chain)      │
├──────────┴──────────┴───────────┴──────────────────────┤
│           PostgreSQL · Redis · RabbitMQ                  │
└─────────────────────────────────────────────────────────┘
```

## 🧮 Mathematical Governance Frameworks

| # | Framework | Category | Description |
|---|-----------|----------|-------------|
| 1 | Action Space Geometry | Safety | Convex hull boundary of allowed actions |
| 2 | Causal Liability Tensor | Liability | Shapley-value responsibility attribution |
| 3 | Reversibility Polytope | Safety | Action undo-ability analysis |
| 4 | Trajectory Anomaly Detection | Anomaly | Mahalanobis distance outlier detection |
| 5 | Behavioral Contracts | Safety | Formal pre/post-condition verification |
| 6 | Cascade Failure Topology | Anomaly | Network centrality & blast radius |
| 7 | Semantic Boundary | Safety | Embedding-based domain enforcement |
| 8 | Intent Alignment | Anomaly | KL/Jensen-Shannon divergence checking |
| 9 | Goal Hijacking Robustness | Safety | Lipschitz-bounded perturbation defense |
| 10 | Multi-Agent Game Theory | Orchestration | Nash equilibrium & cooperation index |
| 11 | Deadlock-Free Scheduling | Orchestration | Banker's algorithm & cycle detection |
| 12 | Optimal Transport | Orchestration | Sinkhorn-regularized task routing |
| 13 | Cryptographic Audit | Compliance | SHA-256 Merkle-chain logging |
| 14 | Causal Responsibility | Compliance | Structural causal model attribution |
| 15 | Formal Compliance Proofs | Compliance | Model checking & property verification |

## 📜 Regulatory Frameworks

- **EU AI Act** — Full compliance evaluation (5 checks)
- **Colorado AI Act (SB 24-205)** — Impact assessment & consumer notification
- **Singapore MGF** — Model AI Governance Framework alignment
- **ISO/IEC 42001** — AI Management System standard

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- (Optional) Docker & Docker Compose

### Development Setup

```bash
# Clone the repository
git clone https://github.com/your-org/fortis-sentinel.ai.git
cd fortis-sentinel.ai

# Backend
cd backend
pip install -r requirements.txt
cp ../.env.example ../.env
uvicorn app:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Docker Compose (Full Stack)

```bash
docker-compose up -d --build
```

This starts: Backend (8000) · Frontend (5173) · PostgreSQL (5432) · Redis (6379) · RabbitMQ (5672/15672)

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/status` | System status with engine info |
| GET/POST | `/api/v1/agents/` | CRUD agent management |
| POST | `/api/v1/agents/{id}/quarantine` | Quarantine an agent |
| GET/POST | `/api/v1/logs/` | Execution log management |
| GET/POST | `/api/v1/governance/policies` | Governance policy CRUD |
| POST | `/api/v1/governance/check/{id}` | Run 15-engine governance check |
| GET | `/api/v1/governance/anomalies` | List detected anomalies |
| POST | `/api/v1/compliance/run` | Run regulatory compliance check |
| GET | `/api/v1/compliance/audit-trail` | Merkle-chain audit trail |
| GET | `/api/v1/compliance/audit-trail/verify/{id}` | Verify chain integrity |
| WS | `/api/v1/ws/feed` | Real-time event WebSocket |

Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## 🔐 Security

- JWT authentication (configurable)
- AES-256 encryption for sensitive data
- Rate limiting (100 req/min default)
- CORS configuration
- Cryptographic hash-chain audit trails (tamper-evident)

## 📁 Project Structure

```
fortis-sentinel.ai/
├── backend/
│   ├── api/          # FastAPI routers (agents, logs, governance, compliance, websocket)
│   ├── engines/      # 15 mathematical governance engines + orchestrator
│   ├── models/       # SQLAlchemy database models
│   ├── schemas/      # Pydantic request/response schemas
│   ├── app.py        # FastAPI application
│   ├── config.py     # Pydantic Settings configuration
│   └── database.py   # SQLAlchemy engine & session factory
├── frontend/
│   └── src/
│       ├── components/  # Sidebar, TopBar
│       ├── pages/       # Dashboard, Agents, Governance, Compliance, Audit
│       └── api.js       # API service layer
├── docker-compose.yml
├── Makefile
└── README.md
```

## 📄 License

MIT License. See [LICENSE.md](LICENSE.md).

---

**Built with** FastAPI · React 18 · SQLAlchemy · NumPy · SciPy
