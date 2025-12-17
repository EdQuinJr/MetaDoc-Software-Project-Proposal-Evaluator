import { useEffect, useState, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Loader, CheckCircle, XCircle } from 'lucide-react';
import Card from '../components/common/Card/Card';
import '../styles/OAuthCallback.css';

const OAuthCallback = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { handleOAuthCallback } = useAuth();
  const [status, setStatus] = useState('processing'); // 'processing', 'success', 'error'
  const [message, setMessage] = useState('Completing authentication...');
  const processed = useRef(false);

  useEffect(() => {
    const processCallback = async () => {
      if (processed.current) return;
      processed.current = true;

      try {
        // Get session token and user data from URL (sent by backend)
        const sessionToken = searchParams.get('session_token');
        const userParam = searchParams.get('user');
        const error = searchParams.get('error');

        if (error) {
          setStatus('error');
          setMessage(`Authentication failed: ${error}`);
          setTimeout(() => navigate('/login'), 3000);
          return;
        }

        if (!sessionToken || !userParam) {
          setStatus('error');
          setMessage('Invalid authentication response');
          setTimeout(() => navigate('/login'), 3000);
          return;
        }

        // Parse user data
        const userData = JSON.parse(decodeURIComponent(userParam));

        // Store session and user data
        handleOAuthCallback(sessionToken, userData);

        setStatus('success');
        setMessage('Login successful! Redirecting to dashboard...');

        // Always redirect to dashboard (professor only)
        localStorage.removeItem('user_type'); // Clean up

        setTimeout(() => {
          navigate('/dashboard');
        }, 3000);
      } catch (error) {
        console.error('OAuth callback error:', error);
        setStatus('error');
        setMessage('An error occurred during authentication');
        setTimeout(() => navigate('/login'), 3000);
      }
    };

    processCallback();
  }, [searchParams, navigate, handleOAuthCallback]);

  return (
    <div className="oauth-callback-page">
      <div className="callback-container">
        <Card className="callback-card-content">
          <div className="text-center">
            {status === 'processing' && (
              <>
                <Loader size={64} className="callback-icon spinner" />
                <h2>Authenticating...</h2>
                <p>{message}</p>
              </>
            )}

            {status === 'success' && (
              <>
                <CheckCircle size={64} className="callback-icon success" />
                <h2>Success!</h2>
                <p>{message}</p>
              </>
            )}

            {status === 'error' && (
              <>
                <XCircle size={64} className="callback-icon error" />
                <h2>Authentication Failed</h2>
                <p>{message}</p>
                <p className="redirect-text">Redirecting to login...</p>
              </>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};

export default OAuthCallback;
