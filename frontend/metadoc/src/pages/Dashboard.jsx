import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { dashboardAPI, authAPI } from '../services/api';
import {
  FileText,
  Clock,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Calendar,
  ArrowRight,
  ExternalLink,
  Copy,
  RefreshCw,
} from 'lucide-react';
import './Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [submissionToken, setSubmissionToken] = useState(null);
  const [tokenLoading, setTokenLoading] = useState(false);
  const [copySuccess, setCopySuccess] = useState(false);
  const [deadlines, setDeadlines] = useState([]);
  const [selectedDeadline, setSelectedDeadline] = useState('');

  useEffect(() => {
    fetchOverview();
    fetchDeadlines();
  }, []);

  const fetchOverview = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await dashboardAPI.getOverview();
      setOverview(response.data);
    } catch (err) {
      console.error('Failed to fetch overview:', err);
      setError('Failed to load dashboard data');
      // Set default empty data to allow dashboard to render
      setOverview({
        total_submissions: 0,
        pending_submissions: 0,
        completed_submissions: 0,
        active_deadlines: 0,
        recent_submissions: [],
        upcoming_deadlines: []
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchDeadlines = async () => {
    try {
      const response = await dashboardAPI.getDeadlines(false); // Only active deadlines
      setDeadlines(response.data.deadlines || []);
    } catch (err) {
      console.error('Failed to fetch deadlines:', err);
    }
  };

  const generateToken = async () => {
    try {
      setTokenLoading(true);
      const deadlineId = selectedDeadline || null;
      const response = await authAPI.generateSubmissionToken(deadlineId);
      setSubmissionToken(response.data.token);
    } catch (err) {
      console.error('Failed to generate token:', err);
      alert('Failed to generate submission token. Please try again.');
    } finally {
      setTokenLoading(false);
    }
  };

  const copySubmissionLink = () => {
    if (!submissionToken) {
      alert('Please generate a token first!');
      return;
    }
    const link = `${window.location.origin}/submit?token=${submissionToken}`;
    navigator.clipboard.writeText(link);
    setCopySuccess(true);
    setTimeout(() => setCopySuccess(false), 2000);
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <AlertCircle size={48} />
        <h3>{error}</h3>
        <button className="btn btn-primary" onClick={fetchOverview}>
          Retry
        </button>
      </div>
    );
  }

  const stats = [
    {
      label: 'Total Submissions',
      value: overview?.total_submissions || 0,
      icon: FileText,
      color: 'maroon',
      change: '+12%',
    },
    {
      label: 'Pending Analysis',
      value: overview?.pending_submissions || 0,
      icon: Clock,
      color: 'gold',
      change: null,
    },
    {
      label: 'Completed',
      value: overview?.completed_submissions || 0,
      icon: CheckCircle,
      color: 'success',
      change: '+8%',
    },
    {
      label: 'Active Deadlines',
      value: overview?.active_deadlines || 0,
      icon: Calendar,
      color: 'info',
      change: null,
    },
  ];

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <div>
          <h1>Dashboard Overview</h1>
          <p className="dashboard-subtitle">
            Welcome back! Monitor student submissions and track deadlines.
          </p>
        </div>
      </div>

      {/* Student Submission Link Banner - Compact */}
      <div className="submission-link-banner-compact">
        <div className="compact-header">
          <ExternalLink size={20} />
          <h3>Student Submission Portal</h3>
        </div>
        
        <div className="compact-content">
          <select 
            value={selectedDeadline} 
            onChange={(e) => setSelectedDeadline(e.target.value)}
            className="compact-select"
          >
            <option value="">No Deadline</option>
            {deadlines.map((deadline) => (
              <option key={deadline.id} value={deadline.id}>
                {deadline.title} - {new Date(deadline.deadline_datetime).toLocaleDateString()}
              </option>
            ))}
          </select>

          <button 
            className="btn-compact btn-generate" 
            onClick={generateToken}
            disabled={tokenLoading}
          >
            {tokenLoading ? <RefreshCw size={16} className="spinning" /> : <ExternalLink size={16} />}
            Generate Link
          </button>

          {submissionToken && (
            <>
              <button 
                className="btn-compact btn-copy" 
                onClick={copySubmissionLink}
              >
                <Copy size={16} />
                {copySuccess ? 'Copied!' : 'Copy'}
              </button>
              <button
                className="btn-compact btn-open"
                onClick={() => window.open(`/submit?token=${submissionToken}`, '_blank')}
              >
                <ExternalLink size={16} />
                Open
              </button>
            </>
          )}
        </div>

        {submissionToken && (
          <div className="compact-token">
            <code>{window.location.origin}/submit?token={submissionToken}</code>
          </div>
        )}
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        {stats.map((stat, index) => (
          <div key={index} className={`stat-card stat-${stat.color}`}>
            <div className="stat-icon">
              <stat.icon size={24} />
            </div>
            <div className="stat-content">
              <p className="stat-label">{stat.label}</p>
              <div className="stat-value-row">
                <h3 className="stat-value">{stat.value}</h3>
                {stat.change && (
                  <span className="stat-change">
                    <TrendingUp size={14} />
                    {stat.change}
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Submissions */}
      <div className="dashboard-section">
        <div className="section-header">
          <h2>Recent Submissions</h2>
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => navigate('/dashboard/submissions')}
          >
            View All
            <ArrowRight size={16} />
          </button>
        </div>

        <div className="card">
          {overview?.recent_submissions?.length > 0 ? (
            <div className="submissions-list">
              {overview.recent_submissions.map((submission) => (
                <div
                  key={submission.id}
                  className="submission-item"
                  onClick={() =>
                    navigate(`/dashboard/submissions/${submission.id}`)
                  }
                >
                  <div className="submission-icon">
                    <FileText size={20} />
                  </div>
                  <div className="submission-details">
                    <h4>{submission.original_filename}</h4>
                    <p className="submission-meta">
                      {submission.student_name || 'Unknown Student'} •{' '}
                      {new Date(submission.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="submission-status">
                    <span className={`badge badge-${getStatusColor(submission.status)}`}>
                      {submission.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <FileText size={48} />
              <h3>No submissions yet</h3>
              <p>Waiting for students to submit their documents</p>
            </div>
          )}
        </div>
      </div>

      {/* Upcoming Deadlines */}
      <div className="dashboard-section">
        <div className="section-header">
          <h2>Upcoming Deadlines</h2>
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => navigate('/dashboard/deadlines')}
          >
            Manage
            <ArrowRight size={16} />
          </button>
        </div>

        <div className="card">
          {overview?.upcoming_deadlines?.length > 0 ? (
            <div className="deadlines-list">
              {overview.upcoming_deadlines.map((deadline) => (
                <div key={deadline.id} className="deadline-item">
                  <div className="deadline-icon">
                    <Calendar size={20} />
                  </div>
                  <div className="deadline-details">
                    <h4>{deadline.title}</h4>
                    <p className="deadline-meta">
                      {new Date(deadline.deadline_datetime).toLocaleDateString()} •{' '}
                      {deadline.submission_count || 0} submissions
                    </p>
                  </div>
                  <div className="deadline-time">
                    <span className="time-remaining">
                      {getTimeRemaining(deadline.deadline_datetime)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <Calendar size={48} />
              <h3>No upcoming deadlines</h3>
              <p>Create a deadline to track submissions</p>
              <button
                className="btn btn-secondary mt-md"
                onClick={() => navigate('/dashboard/deadlines')}
              >
                Create Deadline
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const getStatusColor = (status) => {
  const colors = {
    pending: 'warning',
    processing: 'info',
    completed: 'success',
    failed: 'error',
    warning: 'warning',
  };
  return colors[status] || 'info';
};

const getTimeRemaining = (deadlineDate) => {
  const now = new Date();
  const deadline = new Date(deadlineDate);
  const diff = deadline - now;
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));

  if (days < 0) return 'Overdue';
  if (days === 0) return 'Today';
  if (days === 1) return 'Tomorrow';
  return `${days} days`;
};

export default Dashboard;
