import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { submissionAPI, dashboardAPI } from '../services/api';
import { Upload, Link as LinkIcon, FileText, CheckCircle, AlertCircle, Loader, LogOut, Calendar } from 'lucide-react';
import './StudentSubmit.css';

const StudentSubmit = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('upload'); // 'upload' or 'drive'
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState(null);
  const [deadlines, setDeadlines] = useState([]);

  // Upload form state
  const [file, setFile] = useState(null);
  const [uploadData, setUploadData] = useState({
    student_name: user?.name || '',
    student_email: user?.email || '',
  });

  // Drive link form state
  const [driveData, setDriveData] = useState({
    drive_link: '',
    student_name: user?.name || '',
    student_email: user?.email || '',
  });

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      // Validate file type
      const validTypes = [
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword',
        'application/pdf'
      ];
      const validExtensions = ['.docx', '.doc', '.pdf'];
      const hasValidType = validTypes.includes(selectedFile.type);
      const hasValidExtension = validExtensions.some(ext => selectedFile.name.toLowerCase().endsWith(ext));

      if (!hasValidType && !hasValidExtension) {
        setError('Please select a valid DOCX, DOC, or PDF file');
        setFile(null);
        return;
      }

      // Validate file size (50MB)
      if (selectedFile.size > 50 * 1024 * 1024) {
        setError('File size must be less than 50MB');
        setFile(null);
        return;
      }

      setFile(selectedFile);
      setError(null);
    }
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('student_name', uploadData.student_name);
      formData.append('student_email', uploadData.student_email);

      const response = await submissionAPI.uploadFile(formData);
      
      setSuccess({
        message: 'Document submitted successfully!',
        jobId: response.data.job_id,
      });

      // Reset form
      setFile(null);
      document.getElementById('file-input').value = '';
    } catch (err) {
      console.error('Upload error:', err);
      setError(err.response?.data?.error || 'Failed to submit document. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDriveSubmit = async (e) => {
    e.preventDefault();
    if (!driveData.drive_link.trim()) {
      setError('Please enter a Google Drive link');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await submissionAPI.submitDriveLink(driveData);
      
      setSuccess({
        message: 'Document submitted successfully!',
        jobId: response.data.job_id,
      });

      // Reset form
      setDriveData({
        drive_link: '',
        student_name: user?.name || '',
        student_email: user?.email || '',
      });
    } catch (err) {
      console.error('Drive link error:', err);
      const errorMsg = err.response?.data?.error || 'Failed to submit document. Please try again.';
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  if (success) {
    return (
      <div className="student-submit">
        <div className="success-container">
          <div className="success-card">
            <CheckCircle size={80} className="success-icon" />
            <h2>Submission Successful!</h2>
            <p>{success.message}</p>
            <div className="job-id-box">
              <strong>Tracking ID:</strong>
              <code>{success.jobId}</code>
            </div>
            <p className="success-note">
              Your document has been submitted for evaluation. You will be notified once the analysis is complete.
            </p>
            <button className="btn btn-primary" onClick={() => navigate('/')}>
              Return to Home
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="student-submit">
      <header className="submit-header">
        <div className="header-content">
          <div className="logo-section">
            <FileText size={32} />
            <h1>MetaDoc Submission</h1>
          </div>
          <div className="user-section">
            <div className="user-info">
              <span className="user-name">{user?.name}</span>
              <span className="user-email">{user?.email}</span>
            </div>
            <button className="btn-logout-small" onClick={handleLogout}>
              <LogOut size={18} />
            </button>
          </div>
        </div>
      </header>

      <main className="submit-content">
        <div className="submit-container">
          <h2>Submit Your Document</h2>
          <p className="submit-description">
            Upload your academic document or provide a Google Drive link for evaluation
          </p>

          {error && (
            <div className="alert alert-error">
              <AlertCircle size={20} />
              <span>{error}</span>
            </div>
          )}

          <div className="tabs">
            <button
              className={`tab ${activeTab === 'upload' ? 'tab-active' : ''}`}
              onClick={() => setActiveTab('upload')}
            >
              <Upload size={20} />
              Upload File
            </button>
            <button
              className={`tab ${activeTab === 'drive' ? 'tab-active' : ''}`}
              onClick={() => setActiveTab('drive')}
            >
              <LinkIcon size={20} />
              Google Drive Link
            </button>
          </div>

          <div className="tab-content">
            {activeTab === 'upload' ? (
              <form onSubmit={handleUploadSubmit} className="submit-form">
                <div className="form-group">
                  <label htmlFor="file-input">Select Document *</label>
                  <div className="file-input-wrapper">
                    <input
                      type="file"
                      id="file-input"
                      accept=".doc,.docx,.pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/pdf"
                      onChange={handleFileChange}
                      required
                    />
                    {file && (
                      <div className="file-selected">
                        <FileText size={20} />
                        <span>{file.name}</span>
                        <span className="file-size">
                          ({(file.size / 1024 / 1024).toFixed(2)} MB)
                        </span>
                      </div>
                    )}
                  </div>
                  <small>Accepted formats: DOCX, DOC, PDF (Max 50MB)</small>
                </div>

                <div className="form-group">
                  <label htmlFor="student-name">Your Name *</label>
                  <input
                    type="text"
                    id="student-name"
                    className="form-control"
                    value={uploadData.student_name}
                    onChange={(e) => setUploadData({ ...uploadData, student_name: e.target.value })}
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="student-email">Your Email *</label>
                  <input
                    type="email"
                    id="student-email"
                    className="form-control"
                    value={uploadData.student_email}
                    onChange={(e) => setUploadData({ ...uploadData, student_email: e.target.value })}
                    required
                  />
                </div>

                <button type="submit" className="btn btn-primary btn-submit" disabled={loading}>
                  {loading ? (
                    <>
                      <Loader size={20} className="spinner-icon" />
                      Submitting...
                    </>
                  ) : (
                    <>
                      <Upload size={20} />
                      Submit Document
                    </>
                  )}
                </button>
              </form>
            ) : (
              <form onSubmit={handleDriveSubmit} className="submit-form">
                <div className="form-group">
                  <label htmlFor="drive-link">Google Drive Link *</label>
                  <input
                    type="url"
                    id="drive-link"
                    className="form-control"
                    placeholder="https://drive.google.com/file/d/..."
                    value={driveData.drive_link}
                    onChange={(e) => setDriveData({ ...driveData, drive_link: e.target.value })}
                    required
                  />
                  <small>Make sure the link is set to "Anyone with the link can view"</small>
                </div>

                <div className="form-group">
                  <label htmlFor="drive-student-name">Your Name *</label>
                  <input
                    type="text"
                    id="drive-student-name"
                    className="form-control"
                    value={driveData.student_name}
                    onChange={(e) => setDriveData({ ...driveData, student_name: e.target.value })}
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="drive-student-email">Your Email *</label>
                  <input
                    type="email"
                    id="drive-student-email"
                    className="form-control"
                    value={driveData.student_email}
                    onChange={(e) => setDriveData({ ...driveData, student_email: e.target.value })}
                    required
                  />
                </div>

                <button type="submit" className="btn btn-primary btn-submit" disabled={loading}>
                  {loading ? (
                    <>
                      <Loader size={20} className="spinner-icon" />
                      Submitting...
                    </>
                  ) : (
                    <>
                      <LinkIcon size={20} />
                      Submit Link
                    </>
                  )}
                </button>
              </form>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default StudentSubmit;
