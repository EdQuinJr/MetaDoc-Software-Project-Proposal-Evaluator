import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';
import { getMsalInstance } from '../authConfig';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sessionToken, setSessionToken] = useState(null);

  useEffect(() => {
    // Check for existing session on mount
    const token = localStorage.getItem('session_token');
    const savedUser = localStorage.getItem('user');

    if (token && savedUser) {
      setSessionToken(token);
      setUser(JSON.parse(savedUser));
      setLoading(false);
      // Optional: validate session in background without blocking
      // validateSession(token);
    } else {
      setLoading(false);
    }
  }, []);

  const validateSession = async (token) => {
    try {
      const response = await authAPI.validateSession(token);
      if (response.data.valid) {
        setUser(response.data.user);
        setSessionToken(token);
      } else {
        logout();
      }
    } catch (error) {
      console.error('Session validation failed:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (userType = 'professor', provider = 'google') => {
    try {
      // Store user type and provider to determine redirect after OAuth
      localStorage.setItem('user_type', userType);
      localStorage.setItem('auth_provider', provider);

      if (provider === 'microsoft') {
        // Use client-side MSAL (secret-less PKCE flow)
        const instance = await getMsalInstance();
        const loginResponse = await instance.loginPopup({
          scopes: ["openid", "profile", "email", "User.Read"],
          prompt: "select_account"
        });

        if (loginResponse && loginResponse.idToken) {
          // Send ID token to backend for verification and session creation
          const response = await authAPI.microsoftTokenLogin(loginResponse.idToken, userType);
          if (response.data.session_token) {
            handleOAuthCallback(response.data.session_token, response.data.user);

            // Check for specific redirect after auth
            const redirectPath = localStorage.getItem('redirect_after_auth');
            if (redirectPath) {
              localStorage.removeItem('redirect_after_auth');
              window.location.href = redirectPath;
            }
          }
        }
        return;
      }

      const response = await authAPI.initiateLogin(userType, provider);
      if (response.data.auth_url) {
        // Redirect to OAuth provider
        window.location.href = response.data.auth_url;
      }
    } catch (error) {
      console.error('Login initiation failed:', error);
      throw error;
    }
  };

  const handleOAuthCallback = (token, userData) => {
    console.log('Storing auth data:', { token, userData });
    localStorage.setItem('session_token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setSessionToken(token);
    setUser(userData);
    console.log('Auth state updated, isAuthenticated:', !!userData);
  };

  const logout = async () => {
    try {
      if (sessionToken) {
        await authAPI.logout(sessionToken);
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('session_token');
      localStorage.removeItem('user');
      setSessionToken(null);
      setUser(null);
    }
  };

  const value = {
    user,
    sessionToken,
    loading,
    login,
    logout,
    handleOAuthCallback,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
