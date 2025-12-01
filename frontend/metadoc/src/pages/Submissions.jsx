import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { dashboardAPI } from '../services/api';
import { FileText, Search, Filter, ChevronRight, Link as LinkIcon, Users, Calendar, FileType, Hash, Trash2 } from 'lucide-react';
import './Submissions.css';

const Submissions = () => {
  const navigate = useNavigate();
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 20,
    total: 0,
  });

  useEffect(() => {
    fetchSubmissions();
  }, [statusFilter, pagination.page]);

  const fetchSubmissions = async () => {
    try {
      setLoading(true);
      const params = {
        page: pagination.page,
        per_page: pagination.per_page,
      };
      
      if (statusFilter) {
        params.status = statusFilter;
      }
      
      if (searchTerm) {
        params.student_name = searchTerm;
      }

      const response = await dashboardAPI.getSubmissions(params);
      setSubmissions(response.data.submissions || []);
      setPagination({
        ...pagination,
        total: response.data.total || 0,
      });
    } catch (err) {
      console.error('Failed to fetch submissions:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSubmission = async (e, submissionId, filename) => {
    e.stopPropagation(); // Prevent card click navigation
    
    if (!window.confirm(`Are you sure you want to delete "${filename}"? This action cannot be undone.`)) {
      return;
    }
    
    try {
      await dashboardAPI.deleteSubmission(submissionId);
      // Remove from local state
      setSubmissions(submissions.filter(s => s.id !== submissionId));
      alert('Submission deleted successfully');
    } catch (err) {
      console.error('Failed to delete submission:', err);
      alert('Failed to delete submission. Please try again.');
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    fetchSubmissions();
  };

  const getStatusBadge = (status) => {
    const badges = {
      pending: 'badge-warning',
      processing: 'badge-info',
      completed: 'badge-success',
      failed: 'badge-error',
      warning: 'badge-warning',
    };
    return badges[status] || 'badge-info';
  };

  return (
    <div className="submissions-page">
      <div className="submissions-header">
        <div>
          <h1>Submissions</h1>
          <p>View and manage all document submissions</p>
        </div>
      </div>

      <div className="submissions-filters">
        <form onSubmit={handleSearch} className="search-form">
          <div className="search-input-wrapper">
            <Search size={20} className="search-icon" />
            <input
              type="text"
              className="search-input"
              placeholder="Search by student name..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <button type="submit" className="btn btn-primary">
            Search
          </button>
        </form>

        <div className="filter-group">
          <Filter size={20} />
          <select
            className="filter-select"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="processing">Processing</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading submissions...</p>
        </div>
      ) : submissions.length > 0 ? (
        <>
          <div className="submissions-grid">
            {submissions.map((submission) => (
              <div
                key={submission.id}
                className="submission-card"
                onClick={() => navigate(`/dashboard/submissions/${submission.id}`)}
              >
                <div className="submission-card-header">
                  <div className="submission-icon">
                    <FileText size={24} />
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <span className={`badge ${getStatusBadge(submission.status)}`}>
                      {submission.status}
                    </span>
                    {submission.is_late && (
                      <span className="badge badge-warning">
                        Late
                      </span>
                    )}
                  </div>
                </div>

                <div className="submission-card-body">
                  <h3 className="submission-title">{submission.original_filename}</h3>
                  
                  <div className="submission-info-grid">
                    <div className="info-item">
                      <Users size={16} />
                      <div>
                        <span className="info-label">Student</span>
                        <span className="info-value">{submission.student_name || 'Unknown'}</span>
                      </div>
                    </div>
                    
                    <div className="info-item">
                      <Calendar size={16} />
                      <div>
                        <span className="info-label">Submitted</span>
                        <span className="info-value">
                          {new Date(submission.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                    
                    <div className="info-item">
                      <FileType size={16} />
                      <div>
                        <span className="info-label">Type</span>
                        <span className="info-value">
                          {submission.submission_type === 'drive_link' ? (
                            <><LinkIcon size={12} /> Google Drive</>
                          ) : (
                            <><FileText size={12} /> File Upload</>
                          )}
                        </span>
                      </div>
                    </div>
                    
                    <div className="info-item">
                      <Hash size={16} />
                      <div>
                        <span className="info-label">Word Count</span>
                        <span className="info-value">
                          {submission.analysis_summary?.word_count || 'Analyzing...'}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  {submission.last_modified && (
                    <div className="last-update">
                      <small>Last updated: {new Date(submission.last_modified).toLocaleString()}</small>
                    </div>
                  )}
                </div>

                <div className="submission-card-footer">
                  <span className="view-details">
                    View Details
                    <ChevronRight size={16} />
                  </span>
                  <button
                    className="btn-delete"
                    onClick={(e) => handleDeleteSubmission(e, submission.id, submission.original_filename)}
                    title="Delete submission"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {pagination.total > pagination.per_page && (
            <div className="pagination">
              <button
                className="btn btn-outline btn-sm"
                disabled={pagination.page === 1}
                onClick={() => setPagination({ ...pagination, page: pagination.page - 1 })}
              >
                Previous
              </button>
              <span className="pagination-info">
                Page {pagination.page} of {Math.ceil(pagination.total / pagination.per_page)}
              </span>
              <button
                className="btn btn-outline btn-sm"
                disabled={pagination.page >= Math.ceil(pagination.total / pagination.per_page)}
                onClick={() => setPagination({ ...pagination, page: pagination.page + 1 })}
              >
                Next
              </button>
            </div>
          )}
        </>
      ) : (
        <div className="empty-state">
          <FileText size={64} />
          <h3>No submissions found</h3>
          <p>Try adjusting your search or filters</p>
        </div>
      )}
    </div>
  );
};

export default Submissions;
