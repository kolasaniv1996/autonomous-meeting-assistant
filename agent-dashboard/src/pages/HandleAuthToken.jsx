import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export function HandleAuthTokenPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { token: pathToken } = useParams(); // If token is in path e.g., /auth/token/:token
  const { handleOAuthSuccess } = useAuth();
  const [error, setError] = useState(null);
  const [message, setMessage] = useState('Processing authentication...');

  useEffect(() => {
    let jwtToken = null;

    // Check if token is in path parameter
    if (pathToken) {
      jwtToken = pathToken;
    } else {
      // Check if token is in query parameter
      const queryParams = new URLSearchParams(location.search);
      jwtToken = queryParams.get('token');
    }

    if (jwtToken) {
      setMessage('Authentication successful! Redirecting...');
      const result = handleOAuthSuccess(jwtToken);
      if (result.success) {
        navigate('/'); // Redirect to dashboard or desired page
      } else {
        setError(result.error || 'Failed to process OAuth token.');
      }
    } else {
      setError('No authentication token found in URL.');
      setMessage('');
    }
  }, [location, navigate, handleOAuthSuccess, pathToken]);

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen p-4">
        <h2 className="text-xl font-semibold text-red-600 mb-2">Authentication Error</h2>
        <p className="text-red-500 mb-4 text-center">{error}</p>
        <a href="/login" className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
          Go to Login
        </a>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h2 className="text-xl font-semibold">{message}</h2>
      {/* You could add a spinner here */}
      {!message && !error && <p>Invalid authentication attempt.</p>}
    </div>
  );
}
