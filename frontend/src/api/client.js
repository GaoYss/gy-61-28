const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `请求失败: ${response.status}`);
  }

  return response.json();
}

function unwrapList(payload) {
  return Array.isArray(payload) ? payload : payload.results || [];
}

export const accessApi = {
  stats: () => request("/stats/"),
  devices: () => request("/devices/").then(unwrapList),
  visitors: (status = "") => request(`/visitors/${status ? `?status=${status}` : ""}`).then(unwrapList),
  alarms: (status = "") => request(`/alarms/${status ? `?status=${status}` : ""}`).then(unwrapList),
  doorLogs: (filters = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.set(key, value);
    });
    const query = params.toString();
    return request(`/door-logs/${query ? `?${query}` : ""}`).then(unwrapList);
  },
};
