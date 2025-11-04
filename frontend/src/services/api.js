import axios from 'axios';

// Vite uses import.meta.env instead of process.env
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) =>
    api.post('/auth/login', new URLSearchParams(data), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),
};

// Query API
export const queryAPI = {
  ask: (question, documentIds = null) =>
    api.post('/query/ask', { question, document_ids: documentIds }),
};

// History API
export const historyAPI = {
  getHistory: (limit = 50, skip = 0) =>
    api.get(`/history/?limit=${limit}&skip=${skip}`),
  getStats: () => api.get('/history/stats'),
  search: (query) => api.get(`/history/search?q=${query}`),
  deleteItem: (id) => api.delete(`/history/${id}`),
  clearAll: () => api.delete('/history/'),
};

export default api;