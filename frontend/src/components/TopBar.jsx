import { useLocation } from 'react-router-dom'

const PAGE_TITLES = {
  '/': 'Dashboard',
  '/agents': 'Agent Management',
  '/governance': 'Governance Engine',
  '/compliance': 'Compliance Center',
  '/audit': 'Audit Trail',
}

export default function TopBar() {
  const location = useLocation()
  const title = PAGE_TITLES[location.pathname] || 'FORTIS SENTINEL'

  return (
    <header className="topbar">
      <div className="topbar-left">
        <h1 className="topbar-title">{title}</h1>
        <span className="topbar-breadcrumb">/ {title}</span>
      </div>
      <div className="topbar-right">
        <div className="topbar-status">
          <span className="status-dot"></span>
          All Systems Operational
        </div>
      </div>
    </header>
  )
}
