import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { dashboardAPI, reportsAPI } from '../services/api';
import {
  FileText,
  Search,
  ChevronRight,
  Link as LinkIcon,
  Users,
  Calendar,
  FileType,
  Hash,
  Trash2,
  X,
  AlertTriangle,
  Clock,
  Folder as FolderIcon,
  ArrowLeft,
  Download,
  Archive
} from 'lucide-react';
import '../styles/Folder.css';

const Folder = () => {
  const navigate = useNavigate();
  const location = useLocation();

  // View State: 'folders' | 'files'
  const [viewMode, setViewMode] = useState('folders');

  // Data State
  const [deadlines, setDeadlines] = useState([]);
  const [submissions, setSubmissions] = useState([]);
  const [selectedDeadline, setSelectedDeadline] = useState(null);

  // Loading State
  const [loading, setLoading] = useState(false); // General loading for submissions
  const [deadlinesLoading, setDeadlinesLoading] = useState(true);

  // Filter/Sort State
  const [searchTerm, setSearchTerm] = useState('');
  const [folderSearchTerm, setFolderSearchTerm] = useState('');
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 20,
    total: 0,
  });
  const [sortOption, setSortOption] = useState('newest'); // 'newest', 'oldest', 'a_z'

  // Modal State
  const [showPreviewModal, setShowPreviewModal] = useState(false);
  const [previewSubmission, setPreviewSubmission] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleteType, setDeleteType] = useState('submission'); // 'submission' | 'folder'

  // Initial Fetch
  useEffect(() => {
    fetchDeadlines();
  }, []);

  // Handle deep link from Dashboard
  useEffect(() => {
    if (location.state?.deadlineId && deadlines.length > 0) {
      const targetDeadline = deadlines.find(d => d.id === location.state.deadlineId);
      if (targetDeadline) {
        handleFolderClick(targetDeadline);
        // Clear state to prevent loop when going back to folders
        navigate(location.pathname, { replace: true, state: {} });
      }
    }
  }, [deadlines, location.state, navigate, location.pathname]);

  // Fetch submissions when view mode changes to files or pagination changes
  useEffect(() => {
    if (viewMode === 'files' && selectedDeadline) {
      fetchSubmissions();
    }
  }, [viewMode, pagination.page, selectedDeadline, sortOption]);

  const fetchDeadlines = async () => {
    try {
      setDeadlinesLoading(true);
      const [response] = await Promise.all([
        dashboardAPI.getDeadlines(true), // Include past
        new Promise(resolve => setTimeout(resolve, 1200))
      ]);
      setDeadlines(response.data.deadlines || []);
    } catch (err) {
      console.error('Failed to fetch deadlines:', err);
    } finally {
      setDeadlinesLoading(false);
    }
  };

  const fetchSubmissions = async () => {
    if (!selectedDeadline) return;

    try {
      setLoading(true);
      let sortBy = 'created_at';
      let sortOrder = 'desc';

      if (sortOption === 'oldest') {
        sortOrder = 'asc';
      } else if (sortOption === 'a_z') {
        sortBy = 'filename';
        sortOrder = 'asc';
      }

      const params = {
        page: pagination.page,
        per_page: pagination.per_page,
        deadline_id: selectedDeadline.id,
        sort_by: sortBy,
        sort_order: sortOrder
      };

      if (searchTerm) {
        params.student_id = searchTerm;
      }

      const [response] = await Promise.all([
        dashboardAPI.getSubmissions(params),
        new Promise(resolve => setTimeout(resolve, 1200))
      ]);

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

  // --- ACTIONS ---

  const handleFolderClick = (deadline) => {
    setSelectedDeadline(deadline);
    setViewMode('files');
    setPagination({ ...pagination, page: 1 }); // Reset pagination
    setSearchTerm(''); // Reset search
  };

  const handleBackToFolders = () => {
    setViewMode('folders');
    setSelectedDeadline(null);
    setSubmissions([]); // Clear submissions
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setPagination({ ...pagination, page: 1 });
    fetchSubmissions();
  };

  const handleConfirmDelete = async () => {
    if (!deleteTarget) return;

    try {
      if (deleteType === 'submission') {
        await dashboardAPI.deleteSubmission(deleteTarget.id);
        setSubmissions(submissions.filter(s => s.id !== deleteTarget.id));
      } else if (deleteType === 'folder') {
        await dashboardAPI.deleteDeadline(deleteTarget.id);
        setDeadlines(deadlines.filter(d => d.id !== deleteTarget.id));
      }
      setShowDeleteModal(false);
      setDeleteTarget(null);
    } catch (err) {
      console.error('Delete failed:', err);
      alert(`Failed to delete ${deleteType}`);
    }
  };

  // --- EXPORT LOGIC ---

  const handleExportCSV = async () => {
    if (!selectedDeadline) return;

    try {
      const confirmExport = window.confirm(`Export overview for "${selectedDeadline.title}" as CSV?`);
      if (!confirmExport) return;

      const response = await reportsAPI.exportCSV({
        filters: { deadline_id: selectedDeadline.id }
      });

      if (response.data && response.data.export_id) {
        // Trigger download
        const exportId = response.data.export_id;
        const downloadUrl = `/api/v1/reports/download/${exportId}`;

        // Use authenticated download via API or direct if cookie/token handled? 
        // Best to use the blob approach to ensure auth headers are sent
        const blobResponse = await reportsAPI.downloadExport(exportId);
        const url = window.URL.createObjectURL(new Blob([blobResponse.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', response.data.filename || 'export.csv');
        document.body.appendChild(link);
        link.click();
        link.remove();
      } else {
        alert('Export failed: No export ID returned.');
      }
    } catch (err) {
      console.error('Export failed:', err);
      alert('Failed to generate export. Please try again.');
    }
  };

  // --- PREVIEW LOGIC ---

  const openPreview = async (e, submission) => {
    e.stopPropagation();
    setPreviewSubmission(submission);
    setShowPreviewModal(true);
    setPreviewLoading(true);

    try {
      const response = await dashboardAPI.getSubmissionDetail(submission.id);
      setPreviewSubmission(response.data);
    } catch (err) {
      console.error('Detail fetch failed:', err);
    } finally {
      setPreviewLoading(false);
    }
  };

  // --- HELPERS ---

  const getDurationString = (diffMs) => {
    const diffSeconds = Math.abs(diffMs) / 1000;
    const days = Math.floor(diffSeconds / (3600 * 24));
    const hours = Math.floor((diffSeconds % (3600 * 24)) / 3600);
    const minutes = Math.floor((diffSeconds % 3600) / 60);

    if (days > 0) return `${days} day${days !== 1 ? 's' : ''}`;
    if (hours > 0) return `${hours} hour${hours !== 1 ? 's' : ''}`;
    return `${minutes} minute${minutes !== 1 ? 's' : ''}`;
  };

  const getTimeliness = (submissionDateStr, deadlineDateStr) => {
    if (!deadlineDateStr) return null;
    const subDate = new Date(submissionDateStr);
    const deadDate = new Date(deadlineDateStr);
    const diff = subDate - deadDate; // + is late, - is early

    if (diff > 0) {
      return {
        isLate: true,
        text: 'LATE',
        detail: `Late by ${getDurationString(diff)}`,
        className: 'status-late',
        badgeClass: 'late'
      };
    }
    return {
      isLate: false,
      text: 'ON TIME',
      detail: `Submitted ${getDurationString(diff)} early`,
      className: 'status-ontime',
      badgeClass: 'ontime'
    };
  };

  const handleDownloadZip = async () => {
    if (!selectedDeadline) return;

    try {
      const confirmDownload = window.confirm(`Download all submission files for "${selectedDeadline.title}" as a ZIP?`);
      if (!confirmDownload) return;

      const response = await dashboardAPI.downloadDeadlineFiles(selectedDeadline.id);

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${selectedDeadline.title.replace(/\s+/g, '_')}_Submissions.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Download failed:', err);
      if (err.response && err.response.status === 404) {
        alert('No files available to download.');
      } else {
        alert('Failed to download ZIP archive.');
      }
    }
  };

  // --- RENDER ---

  const renderFolders = () => {
    const filteredDeadlines = deadlines.filter(deadline =>
      deadline.title.toLowerCase().includes(folderSearchTerm.toLowerCase())
    );

    return (
      <div className="folders-section">
        <div className="submissions-header">
          <div>
            <h1>Submissions Folders</h1>
            <p>Select a deadline folder to view student submissions</p>
          </div>
        </div>

        <div className="submissions-filters">
          <div className="search-form">
            <div className="search-input-wrapper">
              <Search size={20} className="search-icon" />
              <input
                type="text"
                className="search-input"
                placeholder="Search folders..."
                value={folderSearchTerm}
                onChange={(e) => setFolderSearchTerm(e.target.value)}
              />
            </div>
          </div>
        </div>

        {deadlinesLoading ? (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading folders...</p>
          </div>
        ) : filteredDeadlines.length === 0 ? (
          <div className="empty-state">
            <FolderIcon size={64} />
            <h3>{folderSearchTerm ? 'No folders match your search' : 'No Folders Created'}</h3>
            <p>{folderSearchTerm ? 'Try a different search term' : 'Create a deadline in "Deadlines" to generate a folder.'}</p>
          </div>
        ) : (
          <div className="folders-grid">
            {filteredDeadlines.map(deadline => {
              const isPast = new Date(deadline.deadline_datetime) < new Date();

              return (
                <div
                  key={deadline.id}
                  className="folder-card"
                  onClick={() => handleFolderClick(deadline)}
                >
                  <div className="folder-header">
                    <div className="folder-icon-wrapper">
                      <FolderIcon size={24} fill="currentColor" fillOpacity={0.2} />
                    </div>
                    <button
                      className="btn-delete-folder"
                      onClick={(e) => {
                        e.stopPropagation();
                        setDeleteTarget({ id: deadline.id, filename: deadline.title }); // reusing filename for title in modal
                        setDeleteType('folder');
                        setShowDeleteModal(true);
                      }}
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                  <h3 className="folder-title">{deadline.title}</h3>
                  <div className="folder-meta">
                    <Calendar size={14} />
                    <span>Due: {new Date(deadline.deadline_datetime).toLocaleDateString()}</span>
                  </div>
                  <div className="folder-stats">
                    <span className="stat-badge">
                      {deadline.submission_count || 0} Files
                    </span>
                    <span className={`stat-badge ${isPast ? 'status-closed' : 'status-active'}`}>
                      {isPast ? 'Closed' : 'Active'}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    );
  };

  const renderFiles = () => (
    <div className="files-section">
      {/* Header with Back Button */}
      <div className="files-view-header">
        <button className="btn-back" onClick={handleBackToFolders}>
          <ArrowLeft size={18} />
          Back to Folders
        </button>
        <div className="folder-info">
          <h2>{selectedDeadline?.title}</h2>
          <p>
            Due: {new Date(selectedDeadline?.deadline_datetime).toLocaleString()}
            {selectedDeadline?.description && ` • ${selectedDeadline.description}`}
          </p>
        </div>
        <button className="btn btn-outline btn-sm ml-auto mr-2" onClick={handleExportCSV}>
          <Download size={16} className="mr-2" />
          Export Overview
        </button>
        <button className="btn btn-primary btn-sm" onClick={handleDownloadZip}>
          <Archive size={16} className="mr-2" />
          Download All Files
        </button>
      </div>

      {/* Filter / Search */}
      <div className="submissions-filters">
        <form onSubmit={handleSearch} className="search-form">
          <div className="search-input-wrapper">
            <Search size={20} className="search-icon" />
            <input
              type="text"
              className="search-input"
              placeholder="Search student ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </form>
        <div className="filter-group">
          <select
            className="filter-select"
            value={sortOption}
            onChange={(e) => {
              setSortOption(e.target.value);
              setPagination({ ...pagination, page: 1 });
            }}
          >
            <option value="newest">Newest Date</option>
            <option value="oldest">Oldest Date</option>
            <option value="a_z">Name (A-Z)</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading submissions...</p>
        </div>
      ) : submissions.length === 0 ? (
        <div className="empty-state">
          <FileText size={64} />
          <h3>No Files Submitted Yet</h3>
          <p>Students haven't submitted anything for this deadline yet.</p>
        </div>
      ) : (
        <>

          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>File Name</th>
                  <th>Student ID</th>
                  <th>Date Submitted</th>
                  <th>Status</th>
                  <th>Type</th>
                  <th>Words</th>
                  <th className="text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {submissions.map(submission => {
                  const timeliness = getTimeliness(submission.created_at, selectedDeadline.deadline_datetime);

                  return (
                    <tr
                      key={submission.id}
                      onClick={() => navigate(`/dashboard/submissions/${submission.id}`)}
                      className="clickable-row"
                    >
                      <td>
                        <div className="file-info-cell">
                          <div
                            className="file-icon-mini clickable-icon"
                            onClick={(e) => openPreview(e, submission)}
                          >
                            <FileText size={18} />
                          </div>
                          <span className="file-name" title={submission.original_filename}>
                            {submission.original_filename}
                          </span>
                        </div>
                      </td>
                      <td>
                        <span className="student-id-pill">
                          <Users size={14} className="icon-subtle" />
                          {submission.student_id || 'N/A'}
                        </span>
                      </td>
                      <td>
                        <div className="date-cell">
                          <Calendar size={14} className="icon-subtle" />
                          {new Date(submission.created_at).toLocaleDateString()}
                          <span className="time-subtle">
                            {new Date(submission.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                        </div>
                      </td>
                      <td>
                        {timeliness && (
                          <div className={`status-pill ${timeliness.isLate ? 'status-late' : 'status-ontime'}`}>
                            {timeliness.isLate ? <AlertTriangle size={12} /> : <Clock size={12} />}
                            <span>{timeliness.text}</span>
                          </div>
                        )}
                      </td>
                      <td>
                        <div className="type-cell">
                          {submission.submission_type === 'drive_link' ? (
                            <><LinkIcon size={14} /> Drive Link</>
                          ) : (
                            <><FileText size={14} /> File Upload</>
                          )}
                        </div>
                      </td>
                      <td>
                        <span className="word-count">
                          {submission.analysis_summary?.word_count || '-'}
                        </span>
                      </td>
                      <td>
                        <div className="actions-cell">
                          <button
                            className="btn-icon btn-view"
                            title="View Details"
                            onClick={(e) => {
                              e.stopPropagation();
                              navigate(`/dashboard/submissions/${submission.id}`);
                            }}
                          >
                            <ChevronRight size={18} />
                          </button>
                          <button
                            className="btn-icon btn-delete-row"
                            title="Delete Submission"
                            onClick={(e) => {
                              e.stopPropagation();
                              setDeleteTarget({ id: submission.id, filename: submission.original_filename });
                              setDeleteType('submission');
                              setShowDeleteModal(true);
                            }}
                          >
                            <Trash2 size={18} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
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
      )}
    </div>
  );

  return (
    <div className="submissions-page">
      {viewMode === 'folders' ? renderFolders() : renderFiles()}

      {/* --- MODALS --- */}

      {/* Preview Modal */}
      {showPreviewModal && (
        <div className="modal-overlay" onClick={() => setShowPreviewModal(false)}>
          <div className="modal-content preview-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>File Preview</h2>
              <button className="btn-close" onClick={() => setShowPreviewModal(false)}>
                <X size={24} />
              </button>
            </div>
            <div className="modal-body">
              {previewLoading ? (
                <div className="loading-state"><div className="spinner"></div></div>
              ) : previewSubmission ? (
                <div className="preview-content-wrapper">
                  <h3 className="preview-title-large">{previewSubmission.original_filename}</h3>

                  <div className="preview-info-row">
                    <span className="preview-info-item"><strong>Student ID:</strong> {previewSubmission.student_id}</span>
                    <span className="preview-info-item"><strong>Submitted:</strong> {new Date(previewSubmission.created_at).toLocaleString()}</span>
                  </div>

                  <div className="preview-info-row">
                    <span className="preview-info-item"><strong>Word Count:</strong> {previewSubmission.analysis_result?.content_statistics?.word_count || 'N/A'}</span>
                  </div>

                  {/* Content Placeholder / Preview */}
                  {!previewSubmission.analysis_result?.document_text ? (
                    <div className="preview-placeholder-large">
                      <FileText size={48} strokeWidth={1} />
                      <p>Document content not available</p>
                      <small>The document may still be processing or content extraction failed.</small>
                    </div>
                  ) : (
                    <div className="document-text-preview">
                      {previewSubmission.analysis_result.document_text}
                    </div>
                  )}

                  <hr className="preview-divider" />

                  {/* Metadata Section */}
                  <div className="preview-section">
                    <h4 className="preview-section-header">Document Metadata:</h4>
                    <div className="metadata-grid-compact">

                      <div className="meta-pair">
                        <span className="meta-label">Author:</span>
                        <span className="meta-val">{previewSubmission.analysis_result?.document_metadata?.author || 'Unknown'}</span>
                      </div>
                      <div className="meta-pair">
                        <span className="meta-label">Creation Date:</span>
                        <span className="meta-val">
                          {(previewSubmission.analysis_result?.document_metadata?.creation_date || previewSubmission.analysis_result?.document_metadata?.created_date)
                            ? new Date(previewSubmission.analysis_result.document_metadata.creation_date || previewSubmission.analysis_result.document_metadata.created_date).toLocaleString()
                            : 'Unknown'}
                        </span>
                      </div>
                      <div className="meta-pair">
                        <span className="meta-label">File Size:</span>
                        <span className="meta-val">
                          {(previewSubmission.file_size / 1024 / 1024).toFixed(2)} MB
                        </span>
                      </div>
                      <div className="meta-pair">
                        <span className="meta-label">Last Editor:</span>
                        <span className="meta-val">{previewSubmission.analysis_result?.document_metadata?.last_editor || 'Unknown'}</span>
                      </div>
                      <div className="meta-pair">
                        <span className="meta-label">Last Modified Date:</span>
                        <span className="meta-val">
                          {(previewSubmission.analysis_result?.document_metadata?.last_modified_date || previewSubmission.analysis_result?.document_metadata?.modified_date)
                            ? new Date(previewSubmission.analysis_result.document_metadata.last_modified_date || previewSubmission.analysis_result.document_metadata.modified_date).toLocaleString()
                            : 'Unknown'}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Contributors Section */}
                  <div className="preview-section">
                    <h4 className="preview-section-header">Contributors:</h4>
                    <div className="contributors-list-simple">
                      {previewSubmission.analysis_result?.document_metadata?.contributors ? (
                        previewSubmission.analysis_result.document_metadata.contributors.map((c, i) => (
                          <div key={i} className="contributor-row">
                            <strong>{c.name}</strong> <span>({c.role || 'Contributor'})</span>
                          </div>
                        ))
                      ) : (
                        <div className="contributor-row">
                          <strong>{previewSubmission.analysis_result?.document_metadata?.author || 'Unknown'}</strong> <span>(Author)</span>
                        </div>
                      )}
                    </div>
                  </div>

                </div>
              ) : (
                <div className="preview-error">Failed to load</div>
              )}
            </div>
            <div className="modal-footer-full">
              <button className="btn btn-primary btn-block" onClick={() => {
                setShowPreviewModal(false);
                navigate(`/dashboard/submissions/${previewSubmission?.id}`);
              }}>
                View Full Details
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Modal */}
      {showDeleteModal && deleteTarget && (
        <div className="modal-overlay" onClick={() => setShowDeleteModal(false)}>
          <div className="modal-content delete-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="delete-icon"><AlertTriangle size={20} /></div>
              <h2>Delete {deleteType === 'folder' ? 'Folder' : 'File'}</h2>
            </div>
            <div className="modal-body">
              <p>Permanently delete <strong>"{deleteTarget.filename}"</strong>?</p>
              {deleteType === 'folder' && (
                <p className="warning-text">This will delete all submissions inside this folder!</p>
              )}
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setShowDeleteModal(false)}>Cancel</button>
              <button className="btn btn-danger" onClick={handleConfirmDelete}>Delete</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Folder;
