import { useState, useEffect } from 'react';
import { submissionAPI } from '../services/api';
import axios from 'axios';
import { Upload, Link as LinkIcon, FileText, CheckCircle, AlertCircle, X, Check } from 'lucide-react';
import Card from '../components/common/Card/Card';
import Input from '../components/common/Input/Input';
import Button from '../components/common/Button/Button';
import '../styles/TokenBasedSubmission.css';

const TokenBasedSubmission = () => {
  const [activeTab, setActiveTab] = useState('upload'); // 'upload' or 'drive'
  const [loading, setLoading] = useState(false);
  const [validating, setValidating] = useState(false);
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState(null);

  // Upload form state
  const [file, setFile] = useState(null);
  const [uploadData, setUploadData] = useState({
    student_id: '',
    student_name: '',
  });

  // Drive link form state
  const [driveData, setDriveData] = useState({
    drive_link: '',
    student_id: '',
    student_name: '',
  });

  const [linkValidation, setLinkValidation] = useState(null);
  const [deadlineInfo, setDeadlineInfo] = useState(null);

  // Get token from URL
  const getTokenFromURL = () => {
    const params = new URLSearchParams(window.location.search);
    return params.get('token');
  };

  // Fetch deadline info when component mounts
  useEffect(() => {
    const fetchDeadlineInfo = async () => {
      const token = getTokenFromURL();
      if (token) {
        try {
          const response = await axios.get(`/api/v1/submission/token-info?token=${token}`);
          if (response.data) {
            setDeadlineInfo(response.data);
          }
        } catch (err) {
          console.error('Failed to fetch deadline info:', err);
        }
      }
    };
    fetchDeadlineInfo();
  }, []);

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

  const handleRemoveFile = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setFile(null);
    setError(null);
    // Reset file input
    const fileInput = document.getElementById('file-input');
    if (fileInput) fileInput.value = '';
  };

  const formatStudentId = (value) => {
    // Remove all non-digits
    const digits = value.replace(/\D/g, '');

    // Format as XX-XXXX-XXX (e.g., 22-1686-452)
    if (digits.length <= 2) {
      return digits;
    } else if (digits.length <= 6) {
      return `${digits.slice(0, 2)}-${digits.slice(2)}`;
    } else {
      return `${digits.slice(0, 2)}-${digits.slice(2, 6)}-${digits.slice(6, 9)}`;
    }
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file');
      return;
    }

    if (!uploadData.student_name.trim()) {
      setError('Please enter your full name');
      return;
    }

    if (!uploadData.student_id.trim()) {
      setError('Please enter your student ID');
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
      formData.append('student_id', uploadData.student_id);
      formData.append('student_name', uploadData.student_name);
      formData.append('token', token);

      const response = await submissionAPI.uploadFile(formData);
      setSuccess({
        message: '✅ Document uploaded and analysis started successfully!',
        jobId: response.data.job_id,
      });

      // Reset form
      setFile(null);
      setUploadData({ student_id: '', student_name: '' });

      // Clear success message after 5 seconds
      setTimeout(() => setSuccess(null), 5000);
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'Failed to upload file';

      // Check for specific error types
      if (errorMessage.includes('empty') || errorMessage.includes('insufficient content')) {
        setError('❌ Document is empty or has insufficient content. Please upload a valid document with text.');
      } else if (errorMessage.includes('Invalid document') || errorMessage.includes('corrupted')) {
        setError('❌ Document is invalid or corrupted. Please check your file and try again.');
      } else if (errorMessage.includes('Cannot read document')) {
        setError('❌ Cannot read document. The file may be password-protected or corrupted.');
      } else {
        setError(`❌ ${errorMessage}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleValidateLink = async () => {
    if (!driveData.drive_link) {
      setError('Please enter a Google Drive link');
      return;
    }

    setValidating(true);
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
      setValidating(false);
    }
  };

  const handleDriveLinkSubmit = async (e) => {
    e.preventDefault();
    if (!driveData.drive_link) {
      setError('Please enter a Google Drive link');
      return;
    }

    if (!driveData.student_name.trim()) {
      setError('Please enter your full name');
      return;
    }

    if (!driveData.student_id.trim()) {
      setError('Please enter your student ID');
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
        message: '✅ Google Drive document retrieved and analysis started successfully!',
        jobId: response.data.job_id,
      });

      // Reset form
      setDriveData({ drive_link: '', student_id: '', student_name: '' });
      setLinkValidation(null);

      // Clear success message after 5 seconds
      setTimeout(() => setSuccess(null), 5000);
    } catch (err) {
      const errorData = err.response?.data;
      if (errorData?.error_type === 'permission_denied') {
        setError({
          message: `❌ ${errorData.error}`,
          guidance: errorData.guidance,
        });
      } else {
        const errorMessage = errorData?.error || 'Failed to submit Google Drive link';

        // Check for specific error types
        if (errorMessage.includes('empty') || errorMessage.includes('insufficient content')) {
          setError('❌ Document is empty or has insufficient content. Please provide a valid document with text.');
        } else if (errorMessage.includes('Invalid document') || errorMessage.includes('corrupted')) {
          setError('❌ Document is invalid or corrupted. Please check your file and try again.');
        } else if (errorMessage.includes('Cannot read document')) {
          setError('❌ Cannot read document. The file may be password-protected or corrupted.');
        } else {
          setError(`❌ ${errorMessage}`);
        }
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="submit-page">
      <Card className="submit-container">
        <div className="submit-header">
          <h2>Submit Your Document</h2>
          {deadlineInfo ? (
            <div className="deadline-info">
              <h3 className="deadline-title">{deadlineInfo.title}</h3>
              {deadlineInfo.description && (
                <p className="deadline-description">{deadlineInfo.description}</p>
              )}
              {deadlineInfo.deadline_datetime && (
                <p className="deadline-date">
                  Due: {new Date(deadlineInfo.deadline_datetime).toLocaleString()}
                </p>
              )}
            </div>
          ) : (
            <p>Upload a DOCX file or provide a Google Drive link for analysis</p>
          )}
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
            <>
              <div className="card-header">
                <h3 className="card-title">Upload Document</h3>
                <p className="text-gray-600 text-sm">
                  Upload a DOCX or DOC file (max 50MB)
                </p>
              </div>

              <form onSubmit={handleUploadSubmit} className="flex flex-col gap-4">
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
                      <div className="file-selected" style={{ position: 'relative' }}>
                        <button
                          type="button"
                          onClick={handleRemoveFile}
                          style={{
                            position: 'absolute',
                            top: '8px',
                            right: '8px',
                            background: 'white',
                            border: '1px solid #e5e7eb',
                            borderRadius: '50%',
                            padding: '4px',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
                          }}
                          aria-label="Remove file"
                        >
                          <X size={16} color="#6b7280" />
                        </button>
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

                <Input
                  label="Full Name"
                  value={uploadData.student_name}
                  onChange={(e) =>
                    setUploadData({ ...uploadData, student_name: e.target.value })
                  }
                  placeholder="e.g., Juan Dela Cruz"
                />

                <Input
                  label="Student ID Number"
                  value={uploadData.student_id}
                  onChange={(e) =>
                    setUploadData({ ...uploadData, student_id: formatStudentId(e.target.value) })
                  }
                  placeholder="e.g., 22-1686-452"
                />

                {error && typeof error === 'string' && (
                  <div className="alert alert-error">
                    <AlertCircle size={20} />
                    <p>{error}</p>
                  </div>
                )}

                <Button
                  type="submit"
                  size="medium"
                  loading={loading}
                  disabled={!file}
                  icon={Upload}
                  className="w-full"
                >
                  Upload Document
                </Button>
              </form>
            </>
          ) : (
            <>
              <div className="card-header flex items-baseline gap-2">
                <h3 className="card-title text-maroon" style={{ color: 'var(--color-maroon)', fontSize: '1.1rem', margin: 0 }}>Google Drive Link</h3>
                <p className="text-gray-600 text-sm" style={{ margin: 0 }}>
                  Provide a link to your Google Docs or DOCX file
                </p>
              </div>

              <form onSubmit={handleDriveLinkSubmit} className="flex flex-col gap-4">
                <div className="form-group">
                  <label className="form-label">GOOGLE DRIVE LINK</label>
                  <div style={{ position: 'relative' }}>
                    <input
                      type="url"
                      name="drive_link"
                      value={driveData.drive_link}
                      onChange={(e) =>
                        setDriveData({ ...driveData, drive_link: e.target.value })
                      }
                      placeholder="https://drive.google.com/file/d/..."
                      className="form-input w-full"
                      style={{ paddingRight: '3rem' }} // Space for the button
                      required
                    />
                    <button
                      type="button"
                      onClick={handleValidateLink}
                      disabled={!driveData.drive_link || validating}
                      className="flex items-center justify-center transition-colors"
                      style={{
                        position: 'absolute',
                        right: 0,
                        top: 0,
                        bottom: 0,
                        backgroundColor: 'var(--color-gold)',
                        width: '3rem',
                        borderTopRightRadius: 'var(--radius-md)',
                        borderBottomRightRadius: 'var(--radius-md)',
                        border: '1px solid var(--color-gray-300)',
                        borderLeft: 'none',
                        cursor: (!driveData.drive_link || validating) ? 'not-allowed' : 'pointer',
                        opacity: (!driveData.drive_link || validating) ? 0.7 : 1
                      }}
                    >
                      {validating ? (
                        <div className="btn-spinner" style={{ color: 'var(--color-maroon)' }}></div>
                      ) : (
                        <Check size={20} color="var(--color-maroon)" strokeWidth={3} />
                      )}
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

                <Input
                  label="FULL NAME"
                  value={driveData.student_name}
                  onChange={(e) =>
                    setDriveData({ ...driveData, student_name: e.target.value })
                  }
                  placeholder="e.g., Juan Dela Cruz"
                  labelClassName="uppercase-label" // If Input supports custom label class or just style via global CSS
                />

                {/* Apply style to FORCE uppercase labels if component doesn't separate it well, 
                    or just pass uppercase string which I did above. */}

                <Input
                  label="STUDENT ID NUMBER"
                  value={driveData.student_id}
                  onChange={(e) =>
                    setDriveData({ ...driveData, student_id: formatStudentId(e.target.value) })
                  }
                  placeholder="e.g., 22-1686-452"
                />

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

                <Button
                  type="submit"
                  size="medium"
                  loading={loading}
                  disabled={!driveData.drive_link}
                  icon={LinkIcon}
                  className="w-full"
                >
                  Submit Link
                </Button>
              </form>
            </>
          )}
        </div>
      </Card>
    </div>

  );
};

export default TokenBasedSubmission;
