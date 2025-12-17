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
  Users,
} from 'lucide-react';
import Table from '../components/common/Table/Table';
import Card from '../components/common/Card/Card';
import Badge from '../components/common/Badge/Badge';
import Modal from '../components/common/Modal/Modal';
import '../styles/Dashboard.css';

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
  const [showErrorModal, setShowErrorModal] = useState(false);
  const [errorMessage, setErrorMessage] = useState({ title: '', body: '' });

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
      const response = await dashboardAPI.getDeadlines(false);
      setDeadlines(response.data.deadlines || []);
    } catch (err) {
      console.error('Failed to fetch deadlines:', err);
    }
  };

  const generateToken = async () => {
    if (deadlines.length === 0) {
      setErrorMessage({
        title: 'No Deadline Found',
        body: 'You need to create a deadline first before generating a submission link. Deadlines help track and organize student submissions effectively.'
      });
      setShowErrorModal(true);
      return;
    }

    if (!selectedDeadline) {
      setErrorMessage({
        title: 'No Deadline Selected',
        body: 'Please select a deadline from the dropdown before generating a submission link. This helps students know which deadline their submission is for.'
      });
      setShowErrorModal(true);
      return;
    }

    try {
      setTokenLoading(true);
      const response = await authAPI.generateSubmissionToken(selectedDeadline);
      setSubmissionToken(response.data.token);
    } catch (err) {
      console.error('Failed to generate token:', err);
      const errorMsg = err.response?.data?.error || 'Failed to generate submission token. Please try again.';
      setErrorMessage({
        title: 'Token Generation Failed',
        body: errorMsg
      });
      setShowErrorModal(true);
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
      </div>
    );
  }

  const resultColumns = [
    {
      header: 'File Name',
      key: 'filename',
      render: (submission) => (
        <div className="file-info-cell">
          <div className="file-icon-mini">
            <FileText size={18} />
          </div>
          <span className="file-name" title={submission.original_filename}>
            {submission.original_filename}
          </span>
        </div>
      )
    },
    {
      header: 'Student ID',
      key: 'student_id',
      render: (submission) => (
        <span className="student-id-pill">
          <Users size={14} className="icon-subtle" />
          {submission.student_id || 'N/A'}
        </span>
      )
    },
    {
      header: 'Date Submitted',
      key: 'date',
      render: (submission) => (
        <div className="date-cell">
          <span>{new Date(submission.created_at).toLocaleDateString()}</span>
          <span className="time-subtle">
            {new Date(submission.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>
      )
    },
    {
      header: 'Status',
      key: 'status',
      render: (submission) => (
        <Badge variant={getStatusColor(submission.status)}>
          {submission.status}
        </Badge>
      )
    }
  ];

  const deadlineColumns = [
    {
      header: 'Deadline Title',
      key: 'title',
      render: (deadline) => (
        <div className="file-info-cell">
          <div className="file-icon-mini">
            <Calendar size={18} />
          </div>
          <span className="file-name" title={deadline.title}>
            {deadline.title}
          </span>
        </div>
      )
    },
    {
      header: 'Due Date',
      key: 'duedate',
      render: (deadline) => (
        <div className="date-cell">
          <span>{new Date(deadline.deadline_datetime).toLocaleDateString()}</span>
          <span className="time-subtle">
            {getTimeRemaining(deadline.deadline_datetime)}
          </span>
        </div>
      )
    },
    {
      header: 'Submissions',
      key: 'submissions',
      render: (deadline) => (
        <Badge variant="info">
          {deadline.submission_count || 0} Submissions
        </Badge>
      )
    },
    {
      header: 'Status',
      key: 'status',
      render: (deadline) => {
        const isClosed = new Date(deadline.deadline_datetime) < new Date();
        return (
          <Badge variant={isClosed ? 'error' : 'success'}>
            {isClosed ? 'Closed' : 'Active'}
          </Badge>
        );
      }
    }
  ];

  const stats = [
    {
      label: 'Total SPPs',
      value: overview?.total_submissions || 0,
      icon: FileText,
      color: 'maroon',
      change: null,
    },
    {
      label: 'Active Deadlines',
      value: overview?.active_deadlines || 0,
      icon: Calendar,
      color: 'info',
      change: null,
    },
  ];

  const modalFooter = errorMessage.title === 'No Deadline Found' ? (
    <button
      type="button"
      className="btn btn-primary"
      onClick={() => {
        setShowErrorModal(false);
        navigate('/dashboard/deadlines');
      }}
    >
      <Calendar size={18} />
      Go to Deadline Management
    </button>
  ) : (
    <button
      type="button"
      className="btn btn-primary"
      onClick={() => setShowErrorModal(false)}
    >
      OK
    </button>
  );

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <div>
          <h1>Dashboard Overview</h1>
          <p className="dashboard-subtitle">
            Welcome back! Monitor student SPP submissions and track deadlines.
          </p>
        </div>
      </div>

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

      <div className="dashboard-section">
        <div className="section-header">
          <h2>Recent SPP Submissions</h2>
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => navigate('/dashboard/submissions')}
          >
            View All
            <ArrowRight size={16} />
          </button>
        </div>

        <Card>
          <Table
            columns={resultColumns.map(c => ({ header: c.header, key: c.key }))}
            data={overview?.recent_submissions || []}
            renderCell={(item, column) => {
              const colDef = resultColumns.find(c => c.key === column.key);
              return colDef ? colDef.render(item) : null;
            }}
            onRowClick={(item) => navigate(`/dashboard/submissions/${item.id}`)}
            emptyMessage="No SPP submissions yet"
          />
        </Card>
      </div>

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

        <Card>
          <Table
            columns={deadlineColumns.map(c => ({ header: c.header, key: c.key }))}
            data={overview?.upcoming_deadlines || []}
            renderCell={(item, column) => {
              const colDef = deadlineColumns.find(c => c.key === column.key);
              return colDef ? colDef.render(item) : null;
            }}
            onRowClick={(item) => navigate('/dashboard/submissions', { state: { deadlineId: item.id } })}
            emptyMessage="No upcoming deadlines"
          />
        </Card>
      </div>

      <Modal
        isOpen={showErrorModal}
        onClose={() => setShowErrorModal(false)}
        title={errorMessage.title}
        type="error"
        footer={modalFooter}
      >
        <p>{errorMessage.body}</p>
      </Modal>
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

  if (diff < 0) return 'Overdue';

  const hours = Math.floor(diff / (1000 * 60 * 60));
  if (hours < 24) return `${hours}h remaining`;

  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const target = new Date(deadline);
  target.setHours(0, 0, 0, 0);

  const calendarDays = Math.round((target - today) / (1000 * 60 * 60 * 24));

  if (calendarDays === 1) return 'Tomorrow';
  return `${calendarDays} days`;
};

export default Dashboard;
