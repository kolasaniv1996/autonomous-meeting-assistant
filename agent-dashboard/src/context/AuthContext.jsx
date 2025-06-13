import React, { createContext, useState, useEffect, useContext } from 'react';
import { API_BASE_URL, fetchWithAuth } from '../utils/api'; // Import fetchWithAuth

const AuthContext = createContext(null);

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem('authToken'));
  const [isAuthenticated, setIsAuthenticated] = useState(!!token);
  const [currentUser, setCurrentUser] = useState(null);
  const [loadingAuth, setLoadingAuth] = useState(true); // To track initial auth loading

  const fetchCurrentUser = async (currentToken) => {
    if (!currentToken) {
      setCurrentUser(null);
      setIsAuthenticated(false);
      setLoadingAuth(false);
      return;
    }
    try {
      // Use fetchWithAuth which implicitly uses the token from localStorage via getAuthToken
      const response = await fetchWithAuth('/me');
      if (response.ok) {
        const userData = await response.json();
        setCurrentUser(userData);
        setIsAuthenticated(true);
      } else {
        // Token might be invalid/expired
        localStorage.removeItem('authToken');
        setToken(null); // This will trigger the useEffect below
        setCurrentUser(null);
        setIsAuthenticated(false);
      }
    } catch (error) {
      console.error('Failed to fetch current user:', error);
      localStorage.removeItem('authToken');
      setToken(null); // Trigger useEffect
      setCurrentUser(null);
      setIsAuthenticated(false);
    } finally {
      setLoadingAuth(false);
    }
  };

  useEffect(() => {
    if (token) {
      localStorage.setItem('authToken', token);
      // setIsAuthenticated(true); // Done by fetchCurrentUser
      fetchCurrentUser(token);
    } else {
      localStorage.removeItem('authToken');
      setCurrentUser(null);
      setIsAuthenticated(false);
      setLoadingAuth(false);
    }
  }, [token]);

  const login = async (email, password) => {
    try {
      // Login doesn't use fetchWithAuth as it's pre-authentication
      const response = await fetch(`${API_BASE_URL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });
      const data = await response.json();
      if (response.ok && data.access_token) {
        setToken(data.access_token); // This will trigger useEffect which calls fetchCurrentUser
        return { success: true };
      } else {
        return { success: false, error: data.msg || 'Login failed' };
      }
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: 'Login request failed' };
    }
  };

  const register = async (username, email, password) => {
    try {
      const response = await fetch(`${API_BASE_URL}/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, email, password }),
      });
      const data = await response.json();
      if (response.ok) {
        // Optionally login directly after registration
        // await login(email, password);
        return { success: true, message: data.msg || 'Registration successful' };
      } else {
        return { success: false, error: data.msg || 'Registration failed' };
      }
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, error: 'Registration request failed' };
    }
  };

  const logout = () => {
    setToken(null); // This will trigger useEffect to clear user data and localStorage
  };

  const loginWithGoogle = () => {
    console.log("Initiating Google Login");
    // Actual logic is redirecting, then handleOAuthSuccess is called from callback page
  };

  const handleOAuthSuccess = (oauthToken) => {
    if (oauthToken) {
      setToken(oauthToken); // This will trigger useEffect which calls fetchCurrentUser
      return { success: true };
    }
    return { success: false, error: "OAuth token not received" };
  };

  // Pass loadingAuth if you want to show a global loader while checking auth
  return (
    <AuthContext.Provider value={{ token, isAuthenticated, currentUser, loadingAuth, login, register, logout, loginWithGoogle, handleOAuthSuccess }}>
      {!loadingAuth && children}
      {/* Or a more sophisticated loading screen: loadingAuth ? <GlobalSpinner /> : children */}
    </AuthContext.Provider>
  );
};
