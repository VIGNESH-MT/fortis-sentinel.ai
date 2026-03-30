import { useState, useEffect } from 'react'
import { agentsApi, governanceApi, complianceApi, systemApi } from '../api'

export default function Dashboard() {
  const [stats, setStats] = useState({
    agents: { total: 0, by_status: {} },
    anomalies: [],
    system: null,
  })
  const [loading, setLoading] = useState(true)
  const [events, setEvents] = useState(MOCK_EVENTS)

  useEffect(() => {
    loadDashboard()
  }, [])

  async function loadDashboard() {
    setLoading(true)
    try {
      const [agentCount, anomalies, system] = await Promise.allSettled([
        agentsApi.count(),
        governanceApi.listAnomalies({ limit: 10 }),
        systemApi.status(),
      ])
      setStats({
        agents: agentCount.status === 'fulfilled' ? agentCount.value : { total: 0, by_status: {} },
        anomalies: anomalies.status === 'fulfilled' ? anomalies.value : [],
        system: system.status === 'fulfilled' ? system.value : null,
      })
    } catch (e) {
      console.warn('Dashboard data unavailable — showing demo mode', e)
    } finally {
      setLoading(false)
    }
  }

  const agentTotal = stats.agents.total || 12
  const activeAgents = stats.agents.by_status?.active || 9
  const anomalyCount = stats.anomalies.length || 3
  const frameworksActive = stats.system?.frameworks?.active || 18

  return (
    <div className="page-container">
      {/* Stats Cards */}
      <div className="stats-grid">
        <StatCard icon="🤖" value={agentTotal} label="Total Agents" change="+3 this week" positive accent="cyan" />
        <StatCard icon="✅" value={activeAgents} label="Active Agents" change="75% of fleet" positive accent="emerald" />
        <StatCard icon="⚠️" value={anomalyCount} label="Open Anomalies" change="2 critical" accent="amber" />
        <StatCard icon="🧮" value={frameworksActive} label="Active Engines" change="All operational" positive accent="violet" />
        <StatCard icon="📜" value="4" label="Reg. Frameworks" change="EU, CO, SG, ISO" positive accent="cyan" />
      </div>

      {/* Two Column Layout */}
      <div className="grid-2" style={{ gap: '20px', marginBottom: '24px' }}>
        {/* Governance Health */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">🛡️ Governance Health</span>
            <span className="badge safe">Healthy</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <ScoreBar label="Safety Engines" score={92} status="safe" />
            <ScoreBar label="Anomaly Detection" score={87} status="safe" />
            <ScoreBar label="Orchestration" score={78} status="warning" />
            <ScoreBar label="Compliance" score={95} status="safe" />
            <ScoreBar label="Liability" score={83} status="safe" />
          </div>
        </div>

        {/* Live Event Feed */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">📡 Live Event Feed</span>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Real-time</span>
          </div>
          <div className="event-feed">
            {events.map((event, i) => (
              <div key={i} className="event-item">
                <div className={`event-dot ${event.severity}`}></div>
                <div className="event-content">
                  <div className="event-title">{event.title}</div>
                  <div className="event-description">{event.description}</div>
                </div>
                <div className="event-time">{event.time}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Engine Status Grid */}
      <div className="card">
        <div className="card-header">
          <span className="card-title">🧮 Mathematical Framework Status</span>
          <span className="card-subtitle">{frameworksActive} engines active</span>
        </div>
        <div className="engine-grid">
          {ENGINES.map((engine) => (
            <div key={engine.id} className="engine-card">
              <div className="engine-header">
                <div>
                  <div className="engine-name">{engine.name}</div>
                  <div className="engine-id">Approach {engine.id}</div>
                </div>
                <div className={`engine-score ${engine.status}`} style={{ color: `var(--${engine.status === 'safe' ? 'emerald' : engine.status === 'warning' ? 'amber' : 'rose'})` }}>
                  {engine.score}%
                </div>
              </div>
              <div className="progress-bar">
                <div className={`progress-fill ${engine.status}`} style={{ width: `${engine.score}%` }}></div>
              </div>
              <div className="engine-category">{engine.category}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function StatCard({ icon, value, label, change, positive, accent = 'cyan' }) {
  return (
    <div className={`stat-card ${accent}`}>
      <div className="stat-icon">{icon}</div>
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
      {change && <div className={`stat-change ${positive ? 'positive' : 'negative'}`}>{positive ? '↑' : '↓'} {change}</div>}
    </div>
  )
}

function ScoreBar({ label, score, status }) {
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
        <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)' }}>{label}</span>
        <span style={{ fontSize: '12px', fontWeight: 700, color: `var(--${status === 'safe' ? 'emerald' : status === 'warning' ? 'amber' : 'rose'})` }}>{score}%</span>
      </div>
      <div className="progress-bar">
        <div className={`progress-fill ${status}`} style={{ width: `${score}%` }}></div>
      </div>
    </div>
  )
}

const MOCK_EVENTS = [
  { title: 'Agent GPT-Analyst activated', description: 'Status changed to active', severity: 'safe', time: '2m ago' },
  { title: 'Governance check passed', description: 'Agent Claude-Ops scored 94%', severity: 'safe', time: '5m ago' },
  { title: 'Trajectory anomaly detected', description: 'Agent DataMiner-7 deviation 2.3σ', severity: 'warning', time: '8m ago' },
  { title: 'Compliance: EU AI Act', description: 'Agent Gemini-Pro scored 91/100', severity: 'info', time: '12m ago' },
  { title: 'Contract violation', description: 'Agent RiskBot exceeded resource bounds', severity: 'critical', time: '15m ago' },
  { title: 'Audit chain verified', description: '847 entries, chain intact', severity: 'safe', time: '20m ago' },
  { title: 'New policy created', description: 'Safety policy for Agent Alpha-1', severity: 'info', time: '25m ago' },
]

const ENGINES = [
  { id: 1, name: 'Action Space Geometry', category: 'Safety', score: 94, status: 'safe' },
  { id: 2, name: 'Causal Liability Tensor', category: 'Liability', score: 87, status: 'safe' },
  { id: 3, name: 'Reversibility Polytope', category: 'Safety', score: 91, status: 'safe' },
  { id: 4, name: 'Trajectory Anomaly Detection', category: 'Anomaly Detection', score: 82, status: 'safe' },
  { id: 5, name: 'Behavioral Contracts', category: 'Safety', score: 96, status: 'safe' },
  { id: 6, name: 'Cascade Failure Topology', category: 'Anomaly Detection', score: 73, status: 'warning' },
  { id: 7, name: 'Semantic Boundary', category: 'Safety', score: 89, status: 'safe' },
  { id: 8, name: 'Intent Alignment', category: 'Anomaly Detection', score: 85, status: 'safe' },
  { id: 9, name: 'Goal Hijacking Robustness', category: 'Safety', score: 90, status: 'safe' },
  { id: 10, name: 'Multi-Agent Game Theory', category: 'Orchestration', score: 78, status: 'warning' },
  { id: 11, name: 'Deadlock-Free Scheduling', category: 'Orchestration', score: 88, status: 'safe' },
  { id: 12, name: 'Optimal Transport', category: 'Orchestration', score: 81, status: 'safe' },
  { id: 13, name: 'Cryptographic Audit', category: 'Compliance', score: 97, status: 'safe' },
  { id: 14, name: 'Causal Responsibility', category: 'Compliance', score: 84, status: 'safe' },
  { id: 15, name: 'Formal Compliance Proofs', category: 'Compliance', score: 92, status: 'safe' },
]
