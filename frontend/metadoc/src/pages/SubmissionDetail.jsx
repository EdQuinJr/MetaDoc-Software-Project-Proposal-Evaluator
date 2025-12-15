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
} from 'lucide-react';
import '../styles/SubmissionDetail.css';

const SubmissionDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [submission, setSubmission] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSubmissionDetail();
  }, [id]);

  const fetchSubmissionDetail = async () => {
    try {
      setLoading(true);
      const response = await dashboardAPI.getSubmissionDetail(id);
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
        <button className="btn btn-primary" onClick={() => navigate('/dashboard/submissions')}>
          Back to SPP Files
        </button>
      </div>
    );
  }

  const analysis = submission.analysis_result;

  return (
    <div className="detail-page">
      <button className="btn btn-ghost mb-lg" onClick={() => navigate('/dashboard/submissions')}>
        <ArrowLeft size={20} />
        Back to SPP Files
      </button>

      <div className="detail-header">
        <div className="detail-title-section">
          <h1>{submission.original_filename}</h1>
          <span className={`badge badge-${getStatusColor(submission.status)}`}>
            {submission.status}
          </span>
        </div>
      </div>

      <div className="detail-grid">
        {/* Basic Information */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">
              <FileText size={20} />
              Basic Information
            </h3>
          </div>
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
        </div>

        {/* Content Statistics */}
        {analysis?.content_statistics && (
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">
                <BarChart3 size={20} />
                Content Statistics
              </h3>
            </div>
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
                <span className="stat-number">{analysis.content_statistics?.estimated_pages || 0}</span>
              </div>
            </div>
          </div>
        )}

        {/* Document Metadata */}
        {analysis?.document_metadata && (
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">
                <User size={20} />
                Document Metadata
              </h3>
            </div>
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">Author</span>
                <span className="info-value">
                  {analysis.document_metadata.author || 'Unavailable'}
                </span>
              </div>
              <div className="info-item">
                <span className="info-label">Created Date</span>
                <span className="info-value">
                  {analysis.document_metadata.creation_date
                    ? new Date(analysis.document_metadata.creation_date).toLocaleString([], {
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
                  {analysis.document_metadata.last_modified_date
                    ? new Date(analysis.document_metadata.last_modified_date).toLocaleString([], {
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
            <div className="card-section">
              <h4 className="section-subtitle">
                <User size={16} />
                Group Members / Contributors
              </h4>
              <div className="contributors-list">
                {(() => {
                  let contributors = [];

                  // Use backend provided contributors list if available
                  if (analysis.document_metadata.contributors && analysis.document_metadata.contributors.length > 0) {
                    contributors = analysis.document_metadata.contributors.map(c => ({
                      name: c.name,
                      role: c.role,
                      date: c.email // Temporary hack: backend doesn't send dates for generic contributors yet, or use creation date fallback
                    }));
                    // Actually, let's keep it simple. If backend has it, use it.
                    // Ensure dates are attached if possible, or fallback to main doc dates
                    contributors = analysis.document_metadata.contributors;
                  } else {
                    // Fallback logic
                    // Add author with creation date
                    if (analysis.document_metadata.author) {
                      contributors.push({
                        name: analysis.document_metadata.author,
                        role: 'Author',
                        date: analysis.document_metadata.creation_date,
                      });
                    }

                    // Add last editor with modification date (if different from author)
                    if (analysis.document_metadata.last_editor &&
                      analysis.document_metadata.last_editor !== analysis.document_metadata.author) {
                      contributors.push({
                        name: analysis.document_metadata.last_editor,
                        role: 'Editor',
                        date: analysis.document_metadata.last_modified_date,
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
                            <span className="contributor-role">({contributor.role})</span>
                          </div>
                          {contributor.date && (
                            <div className="contributor-date">
                              {new Date(contributor.date).toLocaleString([], {
                                year: 'numeric',
                                month: 'numeric',
                                day: 'numeric',
                                hour: 'numeric',
                                minute: '2-digit',
                              })}
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
          </div>
        )}

        {/* Heuristic Insights */}
        {analysis?.heuristic_insights && (
          <div className="card card-full-width">
            <div className="card-header">
              <h3 className="card-title">
                <TrendingUp size={20} />
                Heuristic Insights
              </h3>
            </div>
            <div className="insights-grid">
              {analysis.timeliness_classification && (
                <div className="insight-card">
                  <Clock size={24} className="insight-icon" />
                  <div>
                    <h4>Timeliness</h4>
                    <span className={`badge badge-${getTimelinessColor(analysis.timeliness_classification)}`}>
                      {formatTimeliness(analysis.timeliness_classification)}
                    </span>
                  </div>
                </div>
              )}
              {analysis.contribution_growth_percentage !== null && (
                <div className="insight-card">
                  <TrendingUp size={24} className="insight-icon" />
                  <div>
                    <h4>Contribution Growth</h4>
                    <span className="insight-value">
                      {analysis.contribution_growth_percentage.toFixed(1)}%
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* NLP Analysis */}
        {analysis?.nlp_results && (
          <div className="card card-full-width">
            <div className="card-header">
              <h3 className="card-title">
                <BookOpen size={20} />
                NLP Analysis
              </h3>
            </div>
            <div className="nlp-grid">
              {analysis.flesch_kincaid_score !== null && (
                <div className="nlp-card">
                  <h4>Readability Score</h4>
                  <div className="readability-score">
                    <span className="score-value">{analysis.flesch_kincaid_score.toFixed(1)}</span>
                    <span className="score-label">Flesch-Kincaid</span>
                  </div>
                  {analysis.readability_grade && (
                    <p className="score-grade">Grade Level: {analysis.readability_grade}</p>
                  )}
                </div>
              )}

              {analysis.top_terms && analysis.top_terms.length > 0 && (
                <div className="nlp-card">
                  <h4>Top Terms</h4>
                  <div className="terms-list">
                    {analysis.top_terms.slice(0, 10).map((term, index) => (
                      <span key={index} className="term-badge">
                        {term.term} ({term.frequency})
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {analysis.named_entities && Object.keys(analysis.named_entities).length > 0 && (
                <div className="nlp-card">
                  <h4>Named Entities</h4>
                  <div className="entities-list">
                    {Object.entries(analysis.named_entities).map(([type, count]) => (
                      <div key={type} className="entity-item">
                        <span className="entity-type">{type}</span>
                        <span className="entity-count">{count}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* AI Summary */}
        {analysis?.ai_summary && (
          <div className="card card-full-width">
            <div className="card-header">
              <h3 className="card-title">AI-Generated Summary</h3>
            </div>
            <p className="ai-summary">{analysis.ai_summary}</p>
          </div>
        )}

        {/* Validation Warnings */}
        {analysis?.validation_warnings && analysis.validation_warnings.length > 0 && (
          <div className="card card-full-width">
            <div className="card-header">
              <h3 className="card-title">
                <AlertCircle size={20} />
                Validation Warnings
              </h3>
            </div>
            <div className="warnings-list">
              {analysis.validation_warnings.map((warning, index) => (
                <div key={index} className="warning-item">
                  <AlertCircle size={16} />
                  <span>{warning}</span>
                </div>
              ))}
            </div>
          </div>
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

export default SubmissionDetail;
