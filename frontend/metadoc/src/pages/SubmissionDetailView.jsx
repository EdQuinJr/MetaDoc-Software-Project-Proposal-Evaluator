import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { dashboardAPI } from '../services/api';
import {
  ArrowLeft,
  FileText,
  User,
  Calendar,
  Clock,
  BarChart3,
  BookOpen,
  AlertCircle,
  CheckCircle,
  TrendingUp,
  ExternalLink
} from 'lucide-react';
import Card from '../components/common/Card/Card';
import Badge from '../components/common/Badge/Badge';
import '../styles/SubmissionDetail.css';

const SubmissionDetailView = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [submission, setSubmission] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSubmissionDetail();
  }, [id]);

  /* Ensure loading state lasts at least 2 seconds */
  const fetchSubmissionDetail = async () => {
    try {
      setLoading(true);
      const [response] = await Promise.all([
        dashboardAPI.getSubmissionDetail(id),
        new Promise(resolve => setTimeout(resolve, 1200))
      ]);
      setSubmission(response.data);
    } catch (err) {
      setError('Failed to load submission details');
      console.error('Submission detail error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="detail-loading">
        <div className="spinner"></div>
        <p>Loading submission details...</p>
      </div>
    );
  }

  if (error || !submission) {
    return (
      <div className="detail-error">
        <AlertCircle size={48} />
        <h3>{error || 'Submission not found'}</h3>
        <button className="btn btn-primary" onClick={() => navigate('/dashboard/folders')}>
          Back to Folders
        </button>
      </div>
    );
  }

  const handleBack = () => {
    navigate(-1);
  };

  const handleViewFile = async () => {
    // If it's a Google Drive link, open it directly in a new tab (best for GDocs)
    if (submission.google_drive_link) {
      window.open(submission.google_drive_link, '_blank');
      return;
    }

    try {
      // For file uploads (or fallback), we download/view via API
      const response = await dashboardAPI.getSubmissionFile(id);

      // Create a blob from the response
      const file = new Blob([response.data], { type: submission.mime_type || 'application/pdf' });
      const fileURL = URL.createObjectURL(file);
      window.open(fileURL, '_blank');
    } catch (err) {
      console.error('Error viewing file:', err);

      let errorMessage = 'Failed to open file. It might not exist or there was an error.';

      // Check if the error response is a Blob (since we requested blob)
      if (err.response && err.response.data instanceof Blob) {
        try {
          const text = await err.response.data.text();
          const json = JSON.parse(text);
          if (json.error) errorMessage = json.error;
        } catch (e) {
          // ignore parse error
        }
      } else if (err.response?.data?.error) {
        errorMessage = err.response.data.error;
      }

      alert(errorMessage);
    }
  };

  const analysis = submission.analysis_result;

  return (
    <div className="detail-page">
      <button className="btn btn-ghost mb-lg" onClick={handleBack}>
        <ArrowLeft size={20} />
        Back
      </button>

      <div className="detail-header">
        <div className="detail-title-section">
          <h1 className="text-3xl font-bold text-gray-900">{submission.original_filename}</h1>
          <Badge variant={getStatusColor(submission.status)}>
            {submission.status}
          </Badge>
        </div>

        <button className="btn btn-primary btn-sm" onClick={handleViewFile} title="View original file">
          <ExternalLink size={16} className="mr-2" />
          View Full File
        </button>
      </div>

      <div className="detail-grid">
        {/* Basic Information */}
        <Card title="Basic Information" className="h-full">
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Student Name</span>
              <span className="info-value">{submission.student_name || 'Not provided'}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Student ID</span>
              <span className="info-value">{submission.student_id || 'Not provided'}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Submission Date</span>
              <span className="info-value">
                {new Date(submission.created_at).toLocaleString([], {
                  year: 'numeric',
                  month: 'numeric',
                  day: 'numeric',
                  hour: 'numeric',
                  minute: '2-digit',
                })}
              </span>
            </div>
            <div className="info-item">
              <span className="info-label">File Size</span>
              <span className="info-value">
                {(submission.file_size / 1024 / 1024).toFixed(2)} MB
              </span>
            </div>
            <div className="info-item">
              <span className="info-label">File Type</span>
              <span className="info-value">{submission.mime_type}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Job ID</span>
              <span className="info-value font-mono">{submission.job_id}</span>
            </div>
          </div>
        </Card>

        {/* Content Statistics */}
        {analysis?.content_statistics && (
          <Card title="Content Statistics" className="h-full">
            <div className="stats-list">
              <div className="stat-item">
                <span className="stat-label">Word Count</span>
                <span className="stat-number">{analysis.content_statistics?.word_count || 0}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Character Count</span>
                <span className="stat-number">{analysis.content_statistics?.character_count || 0}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Sentence Count</span>
                <span className="stat-number">{analysis.content_statistics?.sentence_count || 0}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Page Count</span>
                <span className="stat-number">{analysis.content_statistics?.page_count || 0}</span>
              </div>
            </div>
          </Card>
        )}

        {/* Document Metadata */}
        {analysis?.document_metadata && (
          <Card title="Document Metadata" className="h-full">
            <div className="info-grid mb-6">
              <div className="info-item">
                <span className="info-label">Author</span>
                <span className="info-value">
                  {analysis.document_metadata.author || 'Unavailable'}
                </span>
              </div>
              <div className="info-item">
                <span className="info-label">Created Date</span>
                <span className="info-value">
                  {(analysis.document_metadata.created_date || analysis.document_metadata.creation_date)
                    ? new Date(analysis.document_metadata.created_date || analysis.document_metadata.creation_date).toLocaleString([], {
                      year: 'numeric',
                      month: 'numeric',
                      day: 'numeric',
                      hour: 'numeric',
                      minute: '2-digit',
                    })
                    : 'Unavailable'}
                </span>
              </div>
              <div className="info-item">
                <span className="info-label">Last Modified</span>
                <span className="info-value">
                  {(analysis.document_metadata.modified_date || analysis.document_metadata.last_modified_date)
                    ? new Date(analysis.document_metadata.modified_date || analysis.document_metadata.last_modified_date).toLocaleString([], {
                      year: 'numeric',
                      month: 'numeric',
                      day: 'numeric',
                      hour: 'numeric',
                      minute: '2-digit',
                    })
                    : 'Unavailable'}
                </span>
              </div>
              <div className="info-item">
                <span className="info-label">Last Editor</span>
                <span className="info-value">
                  {analysis.document_metadata.last_editor || 'Unavailable'}
                </span>
              </div>
            </div>

            {/* Group Members / Contributors */}
            <div className="pt-6 border-t border-gray-100">
              <h4 className="section-subtitle">
                <User size={16} />
                Group Members / Contributors
              </h4>
              <div className="contributors-list">
                {(() => {
                  let contributors = [];

                  // Use backend provided contributors list if available
                  if (analysis.document_metadata.contributors && analysis.document_metadata.contributors.length > 0) {
                    contributors = analysis.document_metadata.contributors; // Assume simple shape for now
                  } else {
                    // Fallback logic
                    // Add author with creation date
                    // Add author with creation date
                    if (analysis.document_metadata.author) {
                      contributors.push({
                        name: analysis.document_metadata.author,
                        role: 'Author',
                        date: analysis.document_metadata.created_date || analysis.document_metadata.creation_date,
                      });
                    }

                    // Add last editor with modification date (if different from author)
                    if (analysis.document_metadata.last_editor &&
                      analysis.document_metadata.last_editor !== analysis.document_metadata.author) {
                      contributors.push({
                        name: analysis.document_metadata.last_editor,
                        role: 'Editor',
                        date: analysis.document_metadata.modified_date || analysis.document_metadata.last_modified_date,
                      });
                    }
                  }

                  return contributors.length > 0 ? (
                    contributors.map((contributor, index) => (
                      <div key={index} className="contributor-item">
                        <div className="contributor-icon">
                          <User size={14} />
                        </div>
                        <div className="contributor-details">
                          <div className="contributor-name">
                            <strong>{contributor.name}</strong>
                            <span className="contributor-role">({contributor.role || 'Contributor'})</span>
                          </div>
                          {(contributor.date || contributor.email) && (
                            <div className="contributor-date">
                              {contributor.date && !isNaN(Date.parse(contributor.date)) ? new Date(contributor.date).toLocaleString([], {
                                year: 'numeric',
                                month: 'numeric',
                                day: 'numeric',
                                hour: 'numeric',
                                minute: '2-digit',
                              }) : contributor.email}
                            </div>
                          )}
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-muted">No contributor information available</p>
                  );
                })()}
              </div>
            </div>
          </Card>
        )}

        {/* Evaluation Rubric Reference */}
        {submission.deadline?.rubric && (
          <Card title="Evaluation Rubric" className="h-full">
            <div className="mb-4">
              <h4 className="font-bold text-gray-800 text-lg mb-1">{submission.deadline.rubric.title}</h4>
              <p className="text-sm text-gray-500">{submission.deadline.rubric.description}</p>
            </div>

            <div className="overflow-hidden border border-gray-200 rounded-lg">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-1/2">Criteria</th>
                    <th scope="col" className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-1/4">Rating</th>
                    <th scope="col" className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-1/4">Score (0-10)</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {submission.deadline.rubric.criteria?.map((c, idx) => {
                    // Find matching AI evaluation
                    const result = analysis?.ai_insights?.rubric_evaluation?.find(
                      r => r.criteria === c.name || (r.criteria && c.name && r.criteria.toLowerCase().includes(c.name.toLowerCase()))
                    );

                    return (
                      <tr key={idx} className="hover:bg-gray-50 transition-colors">
                        <td className="px-4 py-3 text-sm text-gray-900 align-top">
                          <div className="font-medium text-gray-900">{c.name}</div>
                          <div className="text-xs text-gray-500 mt-1 mb-2" title={c.description}>{c.description}</div>
                          {result?.feedback && (
                            <div className="text-xs text-gray-600 bg-gray-50 p-2 rounded border border-gray-100 italic">
                              "{result.feedback}"
                            </div>
                          )}
                        </td>
                        <td className="px-4 py-3 align-top text-center">
                          {result?.rating ? (
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${result.rating === 'High' ? 'bg-green-100 text-green-800' :
                                result.rating === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                                  'bg-red-100 text-red-800'
                              }`}>
                              {result.rating}
                            </span>
                          ) : (
                            <span className="text-gray-300">-</span>
                          )}
                        </td>
                        <td className="px-4 py-3 align-top text-center font-semibold text-gray-700">
                          {result?.score !== undefined ? result.score : '-'}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </Card>
        )}

        {/* AI Summary and Evaluation */}
        {analysis?.ai_summary && (
          <div className="card-full-width space-y-6">
            <Card title="AI-Generated Summary">
              <p className="ai-summary">{analysis.ai_summary}</p>
            </Card>

            {/* Rubric Evaluation Display */}
            {/* Rubric Evaluation Display (Summary Only) */}
            {analysis.ai_insights?.overall_feedback && (
              <Card title="AI Evaluation Summary">
                <p className="text-gray-700 italic border-l-4 border-blue-500 pl-4 py-2 bg-blue-50 rounded-r-md">
                  "{analysis.ai_insights.overall_feedback}"
                </p>
              </Card>
            )}

            {/* Legacy Overall Score (Only keep if no rating system is used? Or remove entirely if user hates it?) */}
            {/* Keeping it hidden for now based on user request to "fix the rubric" to be low/med/high */}
          </div>
        )}

        {/* Validation Warnings */}
        {analysis?.validation_warnings && analysis.validation_warnings.length > 0 && (
          <Card title="Validation Warnings" className="card-full-width">
            <div className="warnings-list">
              {analysis.validation_warnings.map((warning, index) => (
                <div key={index} className="warning-item">
                  <AlertCircle size={16} />
                  <span>{warning}</span>
                </div>
              ))}
            </div>
          </Card>
        )}
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

const getTimelinessColor = (timeliness) => {
  const colors = {
    on_time: 'success',
    late: 'error',
    last_minute_rush: 'warning',
    no_deadline: 'info',
  };
  return colors[timeliness] || 'info';
};

const formatTimeliness = (timeliness) => {
  const labels = {
    on_time: 'On Time',
    late: 'Late',
    last_minute_rush: 'Last Minute Rush',
    no_deadline: 'No Deadline',
  };
  return labels[timeliness] || timeliness;
};

export default SubmissionDetailView;
