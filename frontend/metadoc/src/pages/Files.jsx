import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { dashboardAPI } from '../services/api';
import { FileText, Search, ChevronRight, Link as LinkIcon, Users, Calendar, FileType, Hash, Trash2, X, Eye, AlertTriangle } from 'lucide-react';
import '../styles/Files.css';

const Files = () => {
  const navigate = useNavigate();
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 20,
    total: 0,
  });
  const [showPreviewModal, setShowPreviewModal] = useState(false);
  const [previewSubmission, setPreviewSubmission] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState(null);

  useEffect(() => {
    fetchSubmissions();
  }, [pagination.page]);

  const fetchSubmissions = async () => {
    try {
      setLoading(true);
      const params = {
        page: pagination.page,
        per_page: pagination.per_page,
      };
      
      if (searchTerm) {
        params.student_id = searchTerm;
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

  const handleDeleteClick = (e, submissionId, filename) => {
    e.stopPropagation(); // Prevent card click navigation
    setDeleteTarget({ id: submissionId, filename });
    setShowDeleteModal(true);
  };

  const handleDeleteConfirm = async () => {
    if (!deleteTarget) return;
    
    try {
      await dashboardAPI.deleteSubmission(deleteTarget.id);
      // Remove from local state
      setSubmissions(submissions.filter(s => s.id !== deleteTarget.id));
      setShowDeleteModal(false);
      setDeleteTarget(null);
    } catch (err) {
      console.error('Failed to delete submission:', err);
      alert('Failed to delete submission. Please try again.');
    }
  };

  const handleDeleteCancel = () => {
    setShowDeleteModal(false);
    setDeleteTarget(null);
  };

  const handleSearch = (e) => {
    e.preventDefault();
    fetchSubmissions();
  };

  const handlePreviewFile = async (e, submission) => {
    e.stopPropagation(); // Prevent card click navigation
    
    setPreviewSubmission(submission);
    setShowPreviewModal(true);
    setPreviewLoading(true);
    
    try {
      // Fetch full submission details with analysis
      const response = await dashboardAPI.getSubmissionDetail(submission.id);
      setPreviewSubmission(response.data);
    } catch (err) {
      console.error('Failed to fetch submission details:', err);
    } finally {
      setPreviewLoading(false);
    }
  };

  const closePreviewModal = () => {
    setShowPreviewModal(false);
    setPreviewSubmission(null);
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
          <h1>Software Project Proposal Documents</h1>
          <p>View and manage all Documents</p>
        </div>
      </div>

      <div className="submissions-filters">
        <form onSubmit={handleSearch} className="search-form">
          <div className="search-input-wrapper">
            <Search size={20} className="search-icon" />
            <input
              type="text"
              className="search-input"
              placeholder="Search by student ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </form>
      </div>

      {loading ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading SPP submissions...</p>
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
                  <div 
                    className="submission-icon clickable-icon" 
                    onClick={(e) => handlePreviewFile(e, submission)}
                    title="Preview file contents"
                  >
                    <FileText size={24} />
                  </div>
                  {submission.is_late && (
                    <span className="badge badge-warning">
                      Late
                    </span>
                  )}
                </div>

                <div className="submission-card-body">
                  <h3 className="submission-title">{submission.original_filename}</h3>
                  
                  <div className="submission-info-grid">
                    <div className="info-item">
                      <Users size={16} />
                      <div>
                        <span className="info-label">Student ID</span>
                        <span className="info-value">{submission.student_id || 'N/A'}</span>
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
                    onClick={(e) => handleDeleteClick(e, submission.id, submission.original_filename)}
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
          <h3>No SPP File found</h3>
          <p>Try adjusting your search or filters</p>
        </div>
      )}

      {/* File Preview Modal */}
      {showPreviewModal && (
        <div className="modal-overlay" onClick={closePreviewModal}>
          <div className="modal-content preview-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>File Preview</h2>
              <button className="btn-close" onClick={closePreviewModal}>
                <X size={24} />
              </button>
            </div>
            
            <div className="modal-body">
              {previewLoading ? (
                <div className="loading-state">
                  <div className="spinner"></div>
                  <p>Loading file contents...</p>
                </div>
              ) : previewSubmission ? (
                <>
                  <div className="preview-header">
                    <h3>{previewSubmission.original_filename}</h3>
                    <div className="preview-meta">
                      <span><strong>Student ID:</strong> {previewSubmission.student_id || 'N/A'}</span>
                      <span><strong>Submitted:</strong> {new Date(previewSubmission.created_at).toLocaleString()}</span>
                      {previewSubmission.analysis_summary && (
                        <span><strong>Word Count:</strong> {previewSubmission.analysis_summary.word_count || 'N/A'}</span>
                      )}
                    </div>
                  </div>

                  {previewSubmission.analysis_result?.document_text ? (
                    <div className="preview-content">
                      <h4>Document Content:</h4>
                      <div className="document-text">
                        {previewSubmission.analysis_result.document_text}
                      </div>
                    </div>
                  ) : (
                    <div className="preview-empty">
                      <FileText size={48} />
                      <p>Document content not available</p>
                      <small>The document may still be processing or content extraction failed.</small>
                    </div>
                  )}

                  {previewSubmission.analysis_result?.document_metadata && (
                    <div className="preview-metadata">
                      <h4>Document Metadata:</h4>
                      <div className="metadata-grid">
                        {Object.entries(previewSubmission.analysis_result.document_metadata).map(([key, value]) => (
                          <div key={key} className="metadata-item">
                            <span className="metadata-label">{key}:</span>
                            <span className="metadata-value">{String(value)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <div className="preview-error">
                  <p>Failed to load file preview</p>
                </div>
              )}
            </div>

            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={closePreviewModal}>
                Close
              </button>
              <button 
                className="btn btn-primary" 
                onClick={() => {
                  closePreviewModal();
                  navigate(`/dashboard/submissions/${previewSubmission?.id}`);
                }}
              >
                View Full Details
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteModal && deleteTarget && (
        <div className="modal-overlay" onClick={handleDeleteCancel}>
          <div className="modal-content delete-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="delete-icon">
                <AlertTriangle size={20} />
              </div>
              <h2>Delete File</h2>
            </div>
            
            <div className="modal-body">
              <p>Are you sure you want to delete <strong>"{deleteTarget.filename}"</strong>?</p>
              <p className="warning-text">This action cannot be undone.</p>
            </div>

            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={handleDeleteCancel}>
                Cancel
              </button>
              <button className="btn btn-danger" onClick={handleDeleteConfirm}>
                <Trash2 size={16} />
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Files;
