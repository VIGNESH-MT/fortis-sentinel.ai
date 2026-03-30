import { useState, useEffect } from 'react'
import { governanceApi, agentsApi } from '../api'

export default function GovernancePage() {
  const [policies, setPolicies] = useState([])
  const [anomalies, setAnomalies] = useState([])
  const [agents, setAgents] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [checkResult, setCheckResult] = useState(null)
  const [form, setForm] = useState({ agent_id: '', policy_name: '', policy_type: 'safety', enforcement_level: 'warning', rules: '' })

  useEffect(() => { loadData() }, [])

  async function loadData() {
    setLoading(true)
    try {
      const [pols, anoms, ags] = await Promise.allSettled([
        governanceApi.listPolicies(),
        governanceApi.listAnomalies({ limit: 20 }),
        agentsApi.list(),
      ])
      setPolicies(pols.status === 'fulfilled' ? pols.value : DEMO_POLICIES)
      setAnomalies(anoms.status === 'fulfilled' ? anoms.value : DEMO_ANOMALIES)
      setAgents(ags.status === 'fulfilled' ? ags.value : [])
    } catch {
      setPolicies(DEMO_POLICIES)
      setAnomalies(DEMO_ANOMALIES)
    } finally {
      setLoading(false)
    }
  }

  async function handleCreate(e) {
    e.preventDefault()
    try {
      await governanceApi.createPolicy(form)
      setShowCreate(false)
      loadData()
    } catch (err) { alert(err.message) }
  }

  async function handleRunCheck(agentId) {
    try {
      const result = await governanceApi.runCheck(agentId)
      setCheckResult(result)
      loadData()
    } catch (err) { alert(err.message) }
  }

  async function handleResolve(id) {
    try {
      await governanceApi.resolveAnomaly(id)
      loadData()
    } catch (err) { alert(err.message) }
  }

  const displayPolicies = policies.length > 0 ? policies : DEMO_POLICIES
  const displayAnomalies = anomalies.length > 0 ? anomalies : DEMO_ANOMALIES

  return (
    <div className="page-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: 800, marginBottom: '4px' }}>Governance Engine</h2>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>15 mathematical frameworks · Policy management</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowCreate(true)}>+ Create Policy</button>
      </div>

      <div className="grid-2" style={{ gap: '20px', marginBottom: '24px' }}>
        {/* Active Policies */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">📋 Active Policies</span>
            <span className="badge info">{displayPolicies.length}</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {displayPolicies.map((p, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px', borderRadius: 'var(--radius-md)', background: 'rgba(17,24,39,0.4)', border: '1px solid var(--border-color)' }}>
                <div>
                  <div style={{ fontSize: '13px', fontWeight: 600 }}>{p.policy_name}</div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>{p.policy_type} · {p.enforcement_level}</div>
                </div>
                <span className={`badge ${p.is_active ? 'active' : 'decommissioned'}`}>{p.is_active ? 'Active' : 'Inactive'}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Anomalies */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">⚠️ Detected Anomalies</span>
            <span className="badge warning">{displayAnomalies.filter(a => !a.resolved).length} open</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '400px', overflowY: 'auto' }}>
            {displayAnomalies.map((a, i) => (
              <div key={i} className="event-item">
                <div className={`event-dot ${a.severity === 'critical' ? 'critical' : a.severity === 'high' ? 'warning' : 'info'}`}></div>
                <div className="event-content">
                  <div className="event-title">{a.anomaly_type?.replace(/_/g, ' ')}</div>
                  <div className="event-description">{a.description}</div>
                  <div style={{ marginTop: '4px', display: 'flex', gap: '6px', alignItems: 'center' }}>
                    <span className={`badge ${a.severity}`}>{a.severity}</span>
                    <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>conf: {((a.confidence || 0) * 100).toFixed(0)}%</span>
                  </div>
                </div>
                {!a.resolved && <button className="btn btn-sm btn-secondary" onClick={() => handleResolve(a.id)}>Resolve</button>}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Check Result */}
      {checkResult && (
        <div className="card" style={{ marginBottom: '24px' }}>
          <div className="card-header">
            <span className="card-title">🧮 Governance Check Result</span>
            <button className="modal-close" onClick={() => setCheckResult(null)}>✕</button>
          </div>
          <div className="stats-grid">
            <StatMini label="Overall Score" value={`${(checkResult.overall_score * 100).toFixed(1)}%`} status={checkResult.status} />
            <StatMini label="Status" value={checkResult.status.toUpperCase()} status={checkResult.status} />
            <StatMini label="Anomalies" value={checkResult.anomalies_detected} status={checkResult.anomalies_detected > 0 ? 'warning' : 'safe'} />
          </div>
        </div>
      )}

      {/* Create Policy Modal */}
      {showCreate && (
        <div className="modal-overlay" onClick={() => setShowCreate(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Create Governance Policy</h3>
              <button className="modal-close" onClick={() => setShowCreate(false)}>✕</button>
            </div>
            <form onSubmit={handleCreate}>
              <div className="form-group">
                <label className="form-label">Agent ID *</label>
                <input className="form-input" required value={form.agent_id} onChange={e => setForm({...form, agent_id: e.target.value})} placeholder="Agent UUID" />
              </div>
              <div className="form-group">
                <label className="form-label">Policy Name *</label>
                <input className="form-input" required value={form.policy_name} onChange={e => setForm({...form, policy_name: e.target.value})} placeholder="e.g., No Delete Operations" />
              </div>
              <div className="form-group">
                <label className="form-label">Policy Type</label>
                <select className="form-select" value={form.policy_type} onChange={e => setForm({...form, policy_type: e.target.value})}>
                  <option value="safety">Safety</option>
                  <option value="compliance">Compliance</option>
                  <option value="operational">Operational</option>
                  <option value="ethical">Ethical</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Enforcement Level</label>
                <select className="form-select" value={form.enforcement_level} onChange={e => setForm({...form, enforcement_level: e.target.value})}>
                  <option value="advisory">Advisory</option>
                  <option value="warning">Warning</option>
                  <option value="blocking">Blocking</option>
                </select>
              </div>
              <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowCreate(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Create Policy</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

function StatMini({ label, value, status }) {
  return (
    <div className={`stat-card ${status === 'safe' ? 'emerald' : status === 'warning' ? 'amber' : 'rose'}`}>
      <div className="stat-value" style={{ fontSize: '22px' }}>{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  )
}

const DEMO_POLICIES = [
  { id: '1', policy_name: 'No Destructive Operations', policy_type: 'safety', enforcement_level: 'blocking', is_active: true },
  { id: '2', policy_name: 'Data Access Logging', policy_type: 'compliance', enforcement_level: 'warning', is_active: true },
  { id: '3', policy_name: 'Rate Limit Enforcement', policy_type: 'operational', enforcement_level: 'blocking', is_active: true },
  { id: '4', policy_name: 'Bias Detection', policy_type: 'ethical', enforcement_level: 'advisory', is_active: true },
]

const DEMO_ANOMALIES = [
  { id: '1', anomaly_type: 'trajectory_deviation', severity: 'high', confidence: 0.87, description: 'Agent DataMiner-7 deviated 2.3σ from normal trajectory', resolved: false },
  { id: '2', anomaly_type: 'contract_violation', severity: 'critical', confidence: 0.95, description: 'RiskBot exceeded resource allocation bounds', resolved: false },
  { id: '3', anomaly_type: 'alignment_drift', severity: 'medium', confidence: 0.62, description: 'Agent behavior diverges from declared intent (JSD=0.34)', resolved: true },
]
