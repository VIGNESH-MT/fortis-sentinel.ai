import { Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import TopBar from './components/TopBar'
import Dashboard from './pages/Dashboard'
import AgentsPage from './pages/AgentsPage'
import GovernancePage from './pages/GovernancePage'
import CompliancePage from './pages/CompliancePage'
import AuditPage from './pages/AuditPage'

export default function App() {
  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-content">
        <TopBar />
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/agents" element={<AgentsPage />} />
          <Route path="/governance" element={<GovernancePage />} />
          <Route path="/compliance" element={<CompliancePage />} />
          <Route path="/audit" element={<AuditPage />} />
        </Routes>
      </div>
    </div>
  )
}
