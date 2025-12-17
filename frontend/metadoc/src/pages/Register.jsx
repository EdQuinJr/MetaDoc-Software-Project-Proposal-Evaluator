import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { FileText, Shield, BarChart3, User, Mail, Lock } from 'lucide-react';
import Input from '../components/common/Input/Input';
import Button from '../components/common/Button/Button';
import '../styles/Register.css';

const Register = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        confirmPassword: ''
    });

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        setError(null);
    };

    const handleFormSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            // Basic Validation
            if (!formData.name.trim()) throw new Error('Name is required');
            if (!formData.email.trim()) throw new Error('Email is required');
            if (formData.password.length < 6) throw new Error('Password must be at least 6 characters');
            if (formData.password !== formData.confirmPassword) throw new Error('Passwords do not match');

            const response = await fetch('http://localhost:5000/api/v1/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: formData.email,
                    password: formData.password,
                    name: formData.name
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Registration failed');
            }

            // On success, redirect to login with a message? 
            // Or just navigate to login
            navigate('/login', { state: { message: 'Registration successful! Please login.' } });
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="register-page">
            <div className="register-container">
                {/* Left Side (Branding) - Shared */}
                <div className="register-left">
                    <div className="brand-header">
                        <div className="brand-icon">
                            <FileText size={48} />
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

                {/* Right Side (Form) */}
                <div className="register-right">
                    <div className="register-card">
                        <div className="register-header">
                            <h2>Create Account</h2>
                            <p>Register to get started</p>
                        </div>

                        {error && (
                            <div className="alert alert-error">
                                <p>{error}</p>
                            </div>
                        )}

                        <form className="register-form" onSubmit={handleFormSubmit}>
                            <Input
                                label="Full Name"
                                name="name"
                                value={formData.name}
                                onChange={handleInputChange}
                                placeholder="Enter your full name"
                                icon={User}
                                required
                            />

                            <Input
                                label="Email Address"
                                name="email"
                                type="email"
                                value={formData.email}
                                onChange={handleInputChange}
                                placeholder="Enter your email"
                                icon={Mail}
                                required
                            />

                            <Input
                                label="Password"
                                name="password"
                                type="password"
                                value={formData.password}
                                onChange={handleInputChange}
                                placeholder="Create a password"
                                icon={Lock}
                                required
                            />

                            <Input
                                label="Confirm Password"
                                name="confirmPassword"
                                type="password"
                                value={formData.confirmPassword}
                                onChange={handleInputChange}
                                placeholder="Confirm your password"
                                icon={Lock}
                                required
                            />

                            <Button type="submit" loading={loading} size="large" className="w-full">
                                Create Account
                            </Button>

                            <div className="auth-switch">
                                <p>
                                    Already have an account?
                                    <Link to="/login" className="link-btn">Sign In</Link>
                                </p>
                            </div>
                        </form>

                        <div className="register-footer">
                            <p>Cebu Institute of Technology - University</p>
                            <p className="text-sm">© 2025 MetaDoc. All rights reserved.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Register;
