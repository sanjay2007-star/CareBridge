import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

// Attach role headers dynamically
export const setAuthHeaders = (role, userId) => {
  api.defaults.headers.common['X-User-Role'] = role;
  api.defaults.headers.common['X-User-Id'] = userId;
};

// Default headers
setAuthHeaders('counsellor', 'COUNS_001');

export default api;
