const API_BASE_URL = 'http://localhost:5001/api';

export const getAuthToken = () => {
  return localStorage.getItem('authToken');
};

export const fetchWithAuth = async (url, options = {}) => {
  const token = getAuthToken();
  const headers = {
    ...options.headers,
    'Content-Type': 'application/json', // Default content type
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    // Token might be expired or invalid, clear it and redirect to login
    localStorage.removeItem('authToken');
    // This assumes you have a way to trigger a redirect globally or use a hook here
    // For simplicity, we'll just log it. A more robust solution would involve AuthContext.
    console.error('Unauthorized access - 401. Token cleared.');
    // window.location.href = '/login'; // This would force a reload and redirect
    // Potentially, call logout() from AuthContext if accessible here, or set a global state.
  }

  return response;
};

export { API_BASE_URL };

