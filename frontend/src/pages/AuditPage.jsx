import { useState, useEffect } from 'react'
import { complianceApi } from '../api'

export default function AuditPage() {
  const [entries, setEntries] = useState([])
  const [verifyResult, setVerifyResult] = useState(null)
  const [loading, setLoading] = useState(true)
  const [verifyId, setVerifyId] = useState('')

  useEffect(() => { loadData() }, [])

  async function loadData() {
    setLoading(true)
    try {
      const data = await complianceApi.auditTrail({ limit: 100 })
      setEntries(data)
    } catch {
      setEntries(DEMO_ENTRIES)
    } finally {
      setLoading(false)
    }
  }

  async function handleVerify() {
    if (!verifyId.trim()) return alert('Enter an Agent ID')
    try {
      const result = await complianceApi.verifyChain(verifyId)
      setVerifyResult(result)
    } catch (err) { alert(err.message) }
  }

  const displayEntries = entries.length > 0 ? entries : DEMO_ENTRIES

  return (
    <div className="page-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: 800, marginBottom: '4px' }}>Cryptographic Audit Trail</h2>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Merkle-chain tamper-evident logging · SHA-256 hash verification</p>
        </div>
      </div>

      {/* Chain Verification */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-header">
          <span className="card-title">🔐 Hash Chain Verification</span>
        </div>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-end', marginBottom: verifyResult ? '16px' : 0 }}>
          <div className="form-group" style={{ flex: 1, marginBottom: 0 }}>
            <label className="form-label">Agent ID</label>
            <input className="form-input" value={verifyId} onChange={e => setVerifyId(e.target.value)} placeholder="Agent UUID to verify chain integrity" />
          </div>
          <button className="btn btn-primary" onClick={handleVerify} style={{ height: '42px' }}>🔍 Verify Chain</button>
        </div>
        {verifyResult && (
          <div style={{ padding: '16px', borderRadius: 'var(--radius-md)', background: verifyResult.valid ? 'var(--emerald-glow)' : 'var(--rose-glow)', border: `1px solid ${verifyResult.valid ? 'rgba(16,185,129,0.3)' : 'rgba(244,63,94,0.3)'}` }}>
            <div style={{ fontSize: '14px', fontWeight: 700, color: verifyResult.valid ? 'var(--emerald)' : 'var(--rose)', marginBottom: '4px' }}>
              {verifyResult.valid ? '✅ Chain Integrity Verified' : '❌ Chain Integrity Compromised'}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
              {verifyResult.message} · {verifyResult.chain_length} entries
            </div>
          </div>
        )}
      </div>

      {/* Audit Entries */}
      <div className="card">
        <div className="card-header">
          <span className="card-title">📜 Audit Entries</span>
          <span className="badge info">{displayEntries.length} entries</span>
        </div>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Event Type</th>
                <th>Agent</th>
                <th>Hash</th>
                <th>Previous Hash</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {displayEntries.map((entry, i) => (
                <tr key={i}>
                  <td>
                    <span className="badge info">{entry.event_type?.replace(/_/g, ' ')}</span>
                  </td>
                  <td style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'monospace' }}>
                    {entry.agent_id?.slice(0, 12)}...
                  </td>
                  <td>
                    <code style={{ fontSize: '10px', color: 'var(--cyan)', background: 'var(--bg-tertiary)', padding: '2px 6px', borderRadius: '4px' }}>
                      {entry.hash?.slice(0, 16)}...
                    </code>
                  </td>
                  <td>
                    <code style={{ fontSize: '10px', color: 'var(--text-muted)', background: 'var(--bg-tertiary)', padding: '2px 6px', borderRadius: '4px' }}>
                      {entry.previous_hash?.slice(0, 16)}...
                    </code>
                  </td>
                  <td style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                    {entry.timestamp ? new Date(entry.timestamp).toLocaleString() : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Chain Visualization */}
      <div className="card" style={{ marginTop: '24px' }}>
        <div className="card-header">
          <span className="card-title">🔗 Hash Chain Visualization</span>
        </div>
        <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', padding: '8px 0' }}>
          {displayEntries.slice(0, 8).map((entry, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
              <div style={{
                padding: '12px 16px',
                background: 'var(--bg-tertiary)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-md)',
                minWidth: '140px',
                textAlign: 'center',
              }}>
                <div style={{ fontSize: '10px', color: 'var(--cyan)', fontFamily: 'monospace', marginBottom: '4px' }}>
                  #{i + 1} · {entry.event_type?.replace(/_/g, ' ')}
                </div>
                <div style={{ fontSize: '9px', color: 'var(--text-muted)', fontFamily: 'monospace' }}>
                  {entry.hash?.slice(0, 12)}...
                </div>
              </div>
              {i < Math.min(displayEntries.length, 8) - 1 && (
                <span style={{ color: 'var(--cyan)', fontSize: '16px' }}>→</span>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

const DEMO_ENTRIES = [
  { id: '1', agent_id: 'a1b2c3d4-e5f6-7890-abcd-ef123456', event_type: 'compliance_check', hash: 'a3f2e1d4c5b6a7f8e9d0c1b2a3f4e5d6c7b8a9f0', previous_hash: '0000000000000000000000000000000000000000', timestamp: '2026-03-30T04:00:00Z' },
  { id: '2', agent_id: 'a1b2c3d4-e5f6-7890-abcd-ef123456', event_type: 'governance_check', hash: 'b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5', previous_hash: 'a3f2e1d4c5b6a7f8e9d0c1b2a3f4e5d6c7b8a9f0', timestamp: '2026-03-30T04:05:00Z' },
  { id: '3', agent_id: 'b2c3d4e5-f6a7-8901-bcde-f1234567', event_type: 'anomaly_detected', hash: 'c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6', previous_hash: 'b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5', timestamp: '2026-03-30T04:10:00Z' },
  { id: '4', agent_id: 'a1b2c3d4-e5f6-7890-abcd-ef123456', event_type: 'policy_change', hash: 'd6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e7', previous_hash: 'c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6', timestamp: '2026-03-30T04:15:00Z' },
  { id: '5', agent_id: 'c3d4e5f6-a7b8-9012-cdef-01234567', event_type: 'status_change', hash: 'e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8', previous_hash: 'd6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e7', timestamp: '2026-03-30T04:20:00Z' },
]
