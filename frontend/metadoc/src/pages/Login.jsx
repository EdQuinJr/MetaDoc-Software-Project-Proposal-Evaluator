import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { LogIn, FileText, Shield, BarChart3 } from 'lucide-react';
import './Login.css';

const Login = () => {
  const { login } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleLogin = async () => {
    setLoading(true);
    setError(null);
    try {
      await login('professor'); // Always login as professor
    } catch (err) {
      setError('Failed to initiate login. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-left">
          <div className="login-branding">
            <div className="logo-container">
              <FileText size={48} className="logo-icon" />
            </div>
            <h1 className="brand-title">MetaDoc</h1>
            <p className="brand-subtitle">
              Google Drive-Integrated Metadata Analyzer for Academic Document Evaluation
            </p>
          </div>

          <div className="features-list">
            <div className="feature-item">
              <div className="feature-icon">
                <FileText size={24} />
              </div>
              <div className="feature-content">
                <h3>Document Analysis</h3>
                <p>Automated metadata extraction and content validation</p>
              </div>
            </div>

            <div className="feature-item">
              <div className="feature-icon">
                <BarChart3 size={24} />
              </div>
              <div className="feature-content">
                <h3>Intelligent Insights</h3>
                <p>Rule-based heuristics and NLP-powered analysis</p>
              </div>
            </div>

            <div className="feature-item">
              <div className="feature-icon">
                <Shield size={24} />
              </div>
              <div className="feature-content">
                <h3>Secure & Compliant</h3>
                <p>Data Privacy Act 2012 compliant with OAuth 2.0</p>
              </div>
            </div>
          </div>
        </div>

        <div className="login-right">
          <div className="login-card">
            <div className="login-header">
              <h2>Welcome Back</h2>
              <p>Sign in with your institutional Gmail account</p>
            </div>

            {error && (
              <div className="alert alert-error">
                <p>{error}</p>
              </div>
            )}

            <div className="login-form">
              <button
                className="btn btn-google"
                onClick={handleLogin}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <div className="spinner-small"></div>
                    <span>Connecting...</span>
                  </>
                ) : (
                  <>
                    <LogIn size={20} />
                    <span>Sign in with Google</span>
                  </>
                )}
              </button>

              <div className="login-divider">
                <span>Secure Authentication</span>
              </div>

              <div className="login-info">
                <p className="info-text">
                  <Shield size={16} />
                  Your credentials are never stored. We use Google OAuth 2.0 for secure authentication.
                </p>
              </div>
            </div>

            <div className="login-footer">
              <p>Cebu Institute of Technology - University</p>
              <p className="text-sm">© 2025 MetaDoc. All rights reserved.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
