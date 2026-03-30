import { NavLink, useLocation } from 'react-router-dom'

const NAV_ITEMS = [
  { section: 'Overview' },
  { path: '/', icon: '📊', label: 'Dashboard' },
  { section: 'Management' },
  { path: '/agents', icon: '🤖', label: 'Agents' },
  { path: '/governance', icon: '🛡️', label: 'Governance' },
  { section: 'Compliance' },
  { path: '/compliance', icon: '✅', label: 'Compliance' },
  { path: '/audit', icon: '🔗', label: 'Audit Trail' },
]

export default function Sidebar() {
  const location = useLocation()

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-icon">🛡️</div>
        <div className="brand-text">
          <span className="brand-name">FORTIS SENTINEL</span>
          <span className="brand-version">v0.1.0 · ALPHA</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item, i) => {
          if (item.section) {
            return <div key={'s' + i} className="sidebar-section-label">{item.section}</div>
          }
          const isActive = location.pathname === item.path
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={`sidebar-link ${isActive ? 'active' : ''}`}
              id={`nav-${item.label.toLowerCase().replace(/\s/g, '-')}`}
            >
              <span className="link-icon">{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          )
        })}
      </nav>

      <div style={{ padding: '16px 20px', borderTop: '1px solid var(--border-color)' }}>
        <div style={{ fontSize: '10px', color: 'var(--text-muted)', lineHeight: '1.6' }}>
          <div>15 Governance Engines</div>
          <div>4 Regulatory Frameworks</div>
          <div style={{ marginTop: '4px', color: 'var(--emerald)' }}>● System Online</div>
        </div>
      </div>
    </aside>
  )
}
