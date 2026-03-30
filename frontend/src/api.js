/**
 * FORTIS SENTINEL - API Service Layer
 * Centralized HTTP client for all backend API calls.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_V1 = `${API_BASE}/api/v1`;

async function request(url, options = {}) {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: res.statusText }));
    throw new Error(err.detail || err.message || `HTTP ${res.status}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

// --- Agents ---
export const agentsApi = {
  list: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`${API_V1}/agents/${qs ? '?' + qs : ''}`);
  },
  count: () => request(`${API_V1}/agents/count`),
  get: (id) => request(`${API_V1}/agents/${id}`),
  create: (data) => request(`${API_V1}/agents/`, { method: 'POST', body: JSON.stringify(data) }),
  update: (id, data) => request(`${API_V1}/agents/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  delete: (id) => request(`${API_V1}/agents/${id}`, { method: 'DELETE' }),
  quarantine: (id) => request(`${API_V1}/agents/${id}/quarantine`, { method: 'POST' }),
  activate: (id) => request(`${API_V1}/agents/${id}/activate`, { method: 'POST' }),
};

// --- Logs ---
export const logsApi = {
  list: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`${API_V1}/logs/${qs ? '?' + qs : ''}`);
  },
  create: (data) => request(`${API_V1}/logs/`, { method: 'POST', body: JSON.stringify(data) }),
  stats: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`${API_V1}/logs/stats${qs ? '?' + qs : ''}`);
  },
};

// --- Governance ---
export const governanceApi = {
  listPolicies: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`${API_V1}/governance/policies${qs ? '?' + qs : ''}`);
  },
  createPolicy: (data) => request(`${API_V1}/governance/policies`, { method: 'POST', body: JSON.stringify(data) }),
  updatePolicy: (id, data) => request(`${API_V1}/governance/policies/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deletePolicy: (id) => request(`${API_V1}/governance/policies/${id}`, { method: 'DELETE' }),
  runCheck: (agentId) => request(`${API_V1}/governance/check/${agentId}`, { method: 'POST' }),
  listAnomalies: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`${API_V1}/governance/anomalies${qs ? '?' + qs : ''}`);
  },
  resolveAnomaly: (id) => request(`${API_V1}/governance/anomalies/${id}/resolve`, { method: 'POST' }),
};

// --- Compliance ---
export const complianceApi = {
  frameworks: () => request(`${API_V1}/compliance/frameworks`),
  run: (data) => request(`${API_V1}/compliance/run`, { method: 'POST', body: JSON.stringify(data) }),
  results: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`${API_V1}/compliance/results${qs ? '?' + qs : ''}`);
  },
  auditTrail: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`${API_V1}/compliance/audit-trail${qs ? '?' + qs : ''}`);
  },
  verifyChain: (agentId) => request(`${API_V1}/compliance/audit-trail/verify/${agentId}`),
};

// --- System ---
export const systemApi = {
  health: () => request(`${API_BASE}/health`),
  status: () => request(`${API_V1}/status`),
};

// --- WebSocket ---
export function createWebSocket(channel = 'all') {
  const wsBase = API_BASE.replace('http', 'ws');
  return new WebSocket(`${wsBase}/api/v1/ws/feed?channel=${channel}`);
}
