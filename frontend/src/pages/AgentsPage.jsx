import { useState, useEffect } from 'react'
import { agentsApi, governanceApi } from '../api'

export default function AgentsPage() {
  const [agents, setAgents] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState({ name: '', description: '', model_type: '', allowed_actions: '', forbidden_actions: '' })

  useEffect(() => { loadAgents() }, [])

  async function loadAgents() {
    setLoading(true)
    try {
      const data = await agentsApi.list()
      setAgents(data)
    } catch {
      setAgents(DEMO_AGENTS)
    } finally {
      setLoading(false)
    }
  }

  async function handleCreate(e) {
    e.preventDefault()
    try {
      await agentsApi.create({
        ...form,
        allowed_actions: form.allowed_actions ? form.allowed_actions.split(',').map(s => s.trim()) : [],
        forbidden_actions: form.forbidden_actions ? form.forbidden_actions.split(',').map(s => s.trim()) : [],
      })
      setShowCreate(false)
      setForm({ name: '', description: '', model_type: '', allowed_actions: '', forbidden_actions: '' })
      loadAgents()
    } catch (err) {
      alert(err.message)
    }
  }

  async function handleQuarantine(id) {
    try {
      await agentsApi.quarantine(id)
      loadAgents()
    } catch (err) { alert(err.message) }
  }

  async function handleActivate(id) {
    try {
      await agentsApi.activate(id)
      loadAgents()
    } catch (err) { alert(err.message) }
  }

  async function handleRunCheck(id) {
    try {
      const result = await governanceApi.runCheck(id)
      alert(`Governance Score: ${(result.overall_score * 100).toFixed(1)}% (${result.status})`)
      loadAgents()
    } catch (err) { alert(err.message) }
  }

  async function handleDelete(id) {
    if (!confirm('Delete this agent and all associated data?')) return
    try {
      await agentsApi.delete(id)
      loadAgents()
    } catch (err) { alert(err.message) }
  }

  const displayAgents = agents.length > 0 ? agents : DEMO_AGENTS

  return (
    <div className="page-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: 800, marginBottom: '4px' }}>AI Agents</h2>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>{displayAgents.length} agents registered</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowCreate(true)} id="btn-create-agent">
          + Register Agent
        </button>
      </div>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Agent</th>
              <th>Model</th>
              <th>Status</th>
              <th>Risk Score</th>
              <th>Health</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {displayAgents.map(agent => (
              <tr key={agent.id}>
                <td>
                  <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{agent.name}</div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>{agent.id?.slice(0, 8)}...</div>
                </td>
                <td>{agent.model_type || '—'}</td>
                <td><span className={`badge ${agent.status}`}>{agent.status}</span></td>
                <td>
                  <ScoreGauge value={agent.risk_score} invert />
                </td>
                <td>
                  <ScoreGauge value={agent.health_score} />
                </td>
                <td>
                  <div style={{ display: 'flex', gap: '6px' }}>
                    <button className="btn btn-secondary btn-sm" onClick={() => handleRunCheck(agent.id)} title="Run Governance Check">🧮</button>
                    {agent.status === 'active' ? (
                      <button className="btn btn-danger btn-sm" onClick={() => handleQuarantine(agent.id)} title="Quarantine">⏸</button>
                    ) : agent.status !== 'decommissioned' ? (
                      <button className="btn btn-secondary btn-sm" onClick={() => handleActivate(agent.id)} title="Activate">▶</button>
                    ) : null}
                    <button className="btn btn-danger btn-sm" onClick={() => handleDelete(agent.id)} title="Delete">✕</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Create Modal */}
      {showCreate && (
        <div className="modal-overlay" onClick={() => setShowCreate(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Register New Agent</h3>
              <button className="modal-close" onClick={() => setShowCreate(false)}>✕</button>
            </div>
            <form onSubmit={handleCreate}>
              <div className="form-group">
                <label className="form-label">Agent Name *</label>
                <input className="form-input" required value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="e.g., GPT-Analyst-v2" id="input-agent-name" />
              </div>
              <div className="form-group">
                <label className="form-label">Description</label>
                <textarea className="form-textarea" value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} placeholder="Purpose and scope of this agent" />
              </div>
              <div className="form-group">
                <label className="form-label">Model Type</label>
                <input className="form-input" value={form.model_type} onChange={e => setForm({ ...form, model_type: e.target.value })} placeholder="e.g., gpt-4, claude-3, gemini-pro" />
              </div>
              <div className="form-group">
                <label className="form-label">Allowed Actions (comma-separated)</label>
                <input className="form-input" value={form.allowed_actions} onChange={e => setForm({ ...form, allowed_actions: e.target.value })} placeholder="read, query, create, list" />
              </div>
              <div className="form-group">
                <label className="form-label">Forbidden Actions (comma-separated)</label>
                <input className="form-input" value={form.forbidden_actions} onChange={e => setForm({ ...form, forbidden_actions: e.target.value })} placeholder="delete, drop, destroy" />
              </div>
              <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowCreate(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" id="btn-submit-agent">Register Agent</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

function ScoreGauge({ value, invert = false }) {
  const pct = Math.round((value || 0) * 100)
  const effectivePct = invert ? 100 - pct : pct
  const status = effectivePct >= 80 ? 'safe' : effectivePct >= 50 ? 'warning' : 'critical'
  return (
    <div className={`score-gauge ${status}`}>
      {invert ? pct : pct}%
    </div>
  )
}

const DEMO_AGENTS = [
  { id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', name: 'GPT-Analyst', model_type: 'gpt-4', status: 'active', risk_score: 0.12, health_score: 0.95 },
  { id: 'b2c3d4e5-f6a7-8901-bcde-f12345678901', name: 'Claude-Ops', model_type: 'claude-3-opus', status: 'active', risk_score: 0.08, health_score: 0.98 },
  { id: 'c3d4e5f6-a7b8-9012-cdef-012345678902', name: 'DataMiner-7', model_type: 'gemini-pro', status: 'quarantined', risk_score: 0.67, health_score: 0.42 },
  { id: 'd4e5f6a7-b8c9-0123-defa-123456789013', name: 'Gemini-Router', model_type: 'gemini-1.5-pro', status: 'active', risk_score: 0.15, health_score: 0.91 },
  { id: 'e5f6a7b8-c9d0-1234-efab-234567890124', name: 'RiskBot-Alpha', model_type: 'gpt-4-turbo', status: 'paused', risk_score: 0.45, health_score: 0.68 },
]
