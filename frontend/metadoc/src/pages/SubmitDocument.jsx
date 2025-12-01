import { useState } from 'react';
import { submissionAPI } from '../services/api';
import { Upload, Link as LinkIcon, FileText, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import './SubmitDocument.css';

const SubmitDocument = () => {
  const [activeTab, setActiveTab] = useState('upload'); // 'upload' or 'drive'
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState(null);

  // Upload form state
  const [file, setFile] = useState(null);
  const [uploadData, setUploadData] = useState({
    student_name: '',
    student_email: '',
  });

  // Drive link form state
  const [driveData, setDriveData] = useState({
    drive_link: '',
    student_name: '',
    student_email: '',
  });

  const [linkValidation, setLinkValidation] = useState(null);

  // Get token from URL
  const getTokenFromURL = () => {
    const params = new URLSearchParams(window.location.search);
    return params.get('token');
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      // Validate file type
      const validTypes = ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword'];
      if (!validTypes.includes(selectedFile.type) && !selectedFile.name.endsWith('.docx') && !selectedFile.name.endsWith('.doc')) {
        setError('Please select a valid DOCX or DOC file');
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

    // Check for token
    const token = getTokenFromURL();
    if (!token) {
      setError('Invalid submission link. Please use the link provided by your professor.');
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
      formData.append('token', token);

      const response = await submissionAPI.uploadFile(formData);
      setSuccess({
        message: 'File uploaded successfully!',
        jobId: response.data.job_id,
      });
      
      // Reset form
      setFile(null);
      setUploadData({ student_name: '', student_email: '' });
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to upload file');
    } finally {
      setLoading(false);
    }
  };

  const handleValidateLink = async () => {
    if (!driveData.drive_link) {
      setError('Please enter a Google Drive link');
      return;
    }

    setLoading(true);
    setLinkValidation(null);
    setError(null);

    try {
      const response = await submissionAPI.validateDriveLink(driveData.drive_link);
      if (response.data.valid) {
        setLinkValidation({
          valid: true,
          fileInfo: response.data.file_info,
        });
      } else {
        setLinkValidation({
          valid: false,
          error: response.data.error,
          guidance: response.data.guidance,
        });
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to validate link');
    } finally {
      setLoading(false);
    }
  };

  const handleDriveLinkSubmit = async (e) => {
    e.preventDefault();
    if (!driveData.drive_link) {
      setError('Please enter a Google Drive link');
      return;
    }

    // Check for token
    const token = getTokenFromURL();
    if (!token) {
      setError('Invalid submission link. Please use the link provided by your professor.');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const submissionData = { ...driveData, token };
      
      const response = await submissionAPI.submitDriveLink(submissionData);
      setSuccess({
        message: 'Google Drive file retrieved successfully!',
        jobId: response.data.job_id,
      });
      
      // Reset form
      setDriveData({ drive_link: '', student_name: '', student_email: '' });
      setLinkValidation(null);
    } catch (err) {
      const errorData = err.response?.data;
      if (errorData?.error_type === 'permission_denied') {
        setError({
          message: errorData.error,
          guidance: errorData.guidance,
        });
      } else {
        setError(errorData?.error || 'Failed to submit Google Drive link');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="submit-page">
      <div className="submit-page-header">
        <div className="branding">
          <FileText size={32} className="brand-icon" />
          <h1 className="brand-name">MetaDoc</h1>
        </div>
        <p className="page-subtitle">Student Document Submission Portal</p>
      </div>

      <div className="submit-container">
        <div className="submit-header">
          <h2>Submit Your Document</h2>
          <p>Upload a DOCX file or provide a Google Drive link for analysis</p>
        </div>

      {!getTokenFromURL() && (
        <div className="alert alert-error">
          <AlertCircle size={20} />
          <div>
            <p className="font-semibold">Invalid Submission Link</p>
            <p className="text-sm">Please use the submission link provided by your professor.</p>
          </div>
        </div>
      )}

      {success && (
        <div className="alert alert-success">
          <CheckCircle size={20} />
          <div>
            <p className="font-semibold">{success.message}</p>
            <p className="text-sm">Job ID: {success.jobId}</p>
          </div>
        </div>
      )}

      <div className="submit-tabs">
        <button
          className={`tab-button ${activeTab === 'upload' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('upload')}
        >
          <Upload size={20} />
          File Upload
        </button>
        <button
          className={`tab-button ${activeTab === 'drive' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('drive')}
        >
          <LinkIcon size={20} />
          Google Drive Link
        </button>
      </div>

      <div className="submit-content">
        {activeTab === 'upload' ? (
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Upload Document</h3>
              <p className="card-description">
                Upload a DOCX or DOC file (max 50MB)
              </p>
            </div>

            <form onSubmit={handleUploadSubmit}>
              <div className="file-upload-area">
                <input
                  type="file"
                  id="file-input"
                  accept=".doc,.docx,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                  onChange={handleFileChange}
                  className="file-input-hidden"
                />
                <label htmlFor="file-input" className="file-upload-label">
                  {file ? (
                    <div className="file-selected">
                      <FileText size={48} />
                      <p className="file-name">{file.name}</p>
                      <p className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>
                  ) : (
                    <div className="file-placeholder">
                      <Upload size={48} />
                      <p className="upload-text">Click to browse or drag and drop</p>
                      <p className="upload-hint">DOCX or DOC files only</p>
                    </div>
                  )}
                </label>
              </div>

              <div className="form-group">
                <label className="form-label">Student Name</label>
                <input
                  type="text"
                  className="form-input"
                  value={uploadData.student_name}
                  onChange={(e) =>
                    setUploadData({ ...uploadData, student_name: e.target.value })
                  }
                  placeholder="Enter student name"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Student Email</label>
                <input
                  type="email"
                  className="form-input"
                  value={uploadData.student_email}
                  onChange={(e) =>
                    setUploadData({ ...uploadData, student_email: e.target.value })
                  }
                  placeholder="student@example.com"
                />
              </div>

              {error && typeof error === 'string' && (
                <div className="alert alert-error">
                  <AlertCircle size={20} />
                  <p>{error}</p>
                </div>
              )}

              <button
                type="submit"
                className="btn btn-primary btn-lg"
                disabled={loading || !file}
              >
                {loading ? (
                  <>
                    <Loader size={20} className="spinner-icon" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload size={20} />
                    Upload Document
                  </>
                )}
              </button>
            </form>
          </div>
        ) : (
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Google Drive Link</h3>
              <p className="card-description">
                Provide a link to your Google Docs or DOCX file
              </p>
            </div>

            <form onSubmit={handleDriveLinkSubmit}>
              <div className="form-group">
                <label className="form-label">Google Drive Link</label>
                <div className="input-with-button">
                  <input
                    type="url"
                    className="form-input"
                    value={driveData.drive_link}
                    onChange={(e) =>
                      setDriveData({ ...driveData, drive_link: e.target.value })
                    }
                    placeholder="https://drive.google.com/file/d/..."
                  />
                  <button
                    type="button"
                    className="btn btn-secondary btn-sm"
                    onClick={handleValidateLink}
                    disabled={loading || !driveData.drive_link}
                  >
                    Validate
                  </button>
                </div>
              </div>

              {linkValidation && (
                <div className={`alert ${linkValidation.valid ? 'alert-success' : 'alert-error'}`}>
                  {linkValidation.valid ? (
                    <>
                      <CheckCircle size={20} />
                      <div>
                        <p className="font-semibold">Link is valid!</p>
                        <p className="text-sm">File: {linkValidation.fileInfo?.name}</p>
                      </div>
                    </>
                  ) : (
                    <>
                      <AlertCircle size={20} />
                      <div>
                        <p className="font-semibold">{linkValidation.error}</p>
                        {linkValidation.guidance && (
                          <div className="guidance-steps">
                            {linkValidation.guidance.steps?.map((step, index) => (
                              <p key={index} className="text-sm">{step}</p>
                            ))}
                          </div>
                        )}
                      </div>
                    </>
                  )}
                </div>
              )}

              <div className="form-group">
                <label className="form-label">Student Name</label>
                <input
                  type="text"
                  className="form-input"
                  value={driveData.student_name}
                  onChange={(e) =>
                    setDriveData({ ...driveData, student_name: e.target.value })
                  }
                  placeholder="Enter student name"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Student Email</label>
                <input
                  type="email"
                  className="form-input"
                  value={driveData.student_email}
                  onChange={(e) =>
                    setDriveData({ ...driveData, student_email: e.target.value })
                  }
                  placeholder="student@example.com"
                />
              </div>

              {error && typeof error === 'object' && (
                <div className="alert alert-error">
                  <AlertCircle size={20} />
                  <div>
                    <p className="font-semibold">{error.message}</p>
                    {error.guidance && (
                      <div className="guidance-steps">
                        {error.guidance.steps?.map((step, index) => (
                          <p key={index} className="text-sm">{step}</p>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {error && typeof error === 'string' && (
                <div className="alert alert-error">
                  <AlertCircle size={20} />
                  <p>{error}</p>
                </div>
              )}

              <button
                type="submit"
                className="btn btn-primary btn-lg"
                disabled={loading || !driveData.drive_link}
              >
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
          </div>
        )}
      </div>
      </div>
    </div>
  );
};

export default SubmitDocument;
