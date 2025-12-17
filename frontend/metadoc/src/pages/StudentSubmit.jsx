import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { submissionAPI } from '../services/api';
import { Upload, Link as LinkIcon, FileText, CheckCircle, AlertCircle, LogOut } from 'lucide-react';
import Card from '../components/common/Card/Card';
import Input from '../components/common/Input/Input';
import Button from '../components/common/Button/Button';
import '../styles/StudentSubmit.css';

const StudentSubmit = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('upload'); // 'upload' or 'drive'
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState(null);

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
          <Card className="success-card text-center">
            <CheckCircle size={80} className="success-icon mb-4 mx-auto" style={{ color: 'var(--color-success)' }} />
            <h2 className="text-2xl font-bold mb-4 text-maroon-dark">Submission Successful!</h2>
            <p className="text-lg mb-6 text-gray-600">{success.message}</p>
            <div className="job-id-box p-6 bg-gray-50 rounded-lg border border-gray-200 mb-6">
              <strong className="block text-sm text-gray-700 uppercase tracking-wide mb-2">Tracking ID:</strong>
              <code className="block text-xl font-mono font-bold text-maroon">{success.jobId}</code>
            </div>
            <p className="text-sm text-gray-600 mb-6">
              Your document has been submitted for evaluation. You will be notified once the analysis is complete.
            </p>
            <Button onClick={() => navigate('/')}>
              Return to Home
            </Button>
          </Card>
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
        <Card className="submit-container">
          <h2 className="text-2xl font-bold mb-2 text-maroon-dark">Submit Your Document</h2>
          <p className="text-gray-600 mb-6">
            Upload your academic document or provide a Google Drive link for evaluation
          </p>

          {error && (
            <div className="alert alert-error mb-4">
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

          <div className="tab-content pt-4">
            {activeTab === 'upload' ? (
              <form onSubmit={handleUploadSubmit} className="submit-form flex flex-col gap-4">
                <div className="form-group mb-4">
                  <label htmlFor="file-input" className="form-label block mb-2 font-medium text-gray-700">Select Document *</label>
                  <div className="file-input-wrapper">
                    <input
                      type="file"
                      id="file-input"
                      accept=".doc,.docx,.pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/pdf"
                      onChange={handleFileChange}
                      required
                      className="w-full p-4 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-maroon hover:bg-gray-50 transition-colors"
                    />
                    {file && (
                      <div className="file-selected flex items-center gap-3 p-3 bg-gray-50 rounded-lg mt-3 text-gray-700">
                        <FileText size={20} className="text-maroon" />
                        <span>{file.name}</span>
                        <span className="file-size ml-auto text-sm text-gray-500">
                          ({(file.size / 1024 / 1024).toFixed(2)} MB)
                        </span>
                      </div>
                    )}
                  </div>
                  <small className="block mt-2 text-gray-500">Accepted formats: DOCX, DOC, PDF (Max 50MB)</small>
                </div>

                <Input
                  label="Your Name"
                  id="student-name"
                  value={uploadData.student_name}
                  onChange={(e) => setUploadData({ ...uploadData, student_name: e.target.value })}
                  required
                />

                <Input
                  label="Your Email"
                  type="email"
                  id="student-email"
                  value={uploadData.student_email}
                  onChange={(e) => setUploadData({ ...uploadData, student_email: e.target.value })}
                  required
                />

                <Button type="submit" loading={loading} icon={Upload} className="w-full mt-4">
                  Submit Document
                </Button>
              </form>
            ) : (
              <form onSubmit={handleDriveSubmit} className="submit-form flex flex-col gap-4">
                <Input
                  label="Google Drive Link"
                  type="url"
                  id="drive-link"
                  placeholder="https://drive.google.com/file/d/..."
                  value={driveData.drive_link}
                  onChange={(e) => setDriveData({ ...driveData, drive_link: e.target.value })}
                  required
                />
                <small className="block -mt-3 mb-2 text-gray-500">Make sure the link is set to "Anyone with the link can view"</small>

                <Input
                  label="Your Name"
                  id="drive-student-name"
                  value={driveData.student_name}
                  onChange={(e) => setDriveData({ ...driveData, student_name: e.target.value })}
                  required
                />

                <Input
                  label="Your Email"
                  type="email"
                  id="drive-student-email"
                  value={driveData.student_email}
                  onChange={(e) => setDriveData({ ...driveData, student_email: e.target.value })}
                  required
                />

                <Button type="submit" loading={loading} icon={LinkIcon} className="w-full mt-4">
                  Submit Link
                </Button>
              </form>
            )}
          </div>
        </Card>
      </main>
    </div>
  );
};

export default StudentSubmit;
