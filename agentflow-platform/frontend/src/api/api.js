import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

export const agentsApi = {
  list: () => api.get('/agents').then(res => res.data),
  listTools: () => api.get('/agents/tools').then(res => res.data),
  get: (id) => api.get(`/agents/${id}`).then(res => res.data),
  create: (data) => api.post('/agents', data).then(res => res.data),
  update: (id, data) => api.put(`/agents/${id}`, data).then(res => res.data),
  delete: (id) => api.delete(`/agents/${id}`).then(res => res.data),
};

export const workflowsApi = {
  list: () => api.get('/workflows').then(res => res.data),
  get: (id) => api.get(`/workflows/${id}`).then(res => res.data),
  create: (data) => api.post('/workflows', data).then(res => res.data),
  delete: (id) => api.delete(`/workflows/${id}`).then(res => res.data),
  execute: (id, message) => api.post(`/runs/${id}/execute`, { message }).then(res => res.data),
};

export const runsApi = {
  list: () => api.get('/runs').then(res => res.data),
  getMessages: (runId) => api.get(`/messages/${runId}`).then(res => res.data),
};

export default api;
