import axios from 'axios';

// Use relative URL in development to leverage Vite proxy, absolute URL in production
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('session_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('session_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  initiateLogin: (userType = 'professor') => api.get('/auth/login', { params: { user_type: userType } }),
  validateSession: (sessionToken) => api.post('/auth/validate', { session_token: sessionToken }),
  logout: (sessionToken) => api.post('/auth/logout', { session_token: sessionToken }),
  getProfile: () => api.get('/auth/profile'),
  generateSubmissionToken: (deadlineId = null) => api.post('/auth/generate-submission-token', { deadline_id: deadlineId }),
};

// Submission API
export const submissionAPI = {
  uploadFile: (formData) => {
    return api.post('/submission/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  submitDriveLink: (data) => api.post('/submission/drive-link', data),
  getStatus: (jobId) => api.get(`/submission/status/${jobId}`),
  validateDriveLink: (driveLink) => api.post('/submission/validate-link', { drive_link: driveLink }),
};

// Dashboard API
export const dashboardAPI = {
  getOverview: () => api.get('/dashboard/overview'),
  getSubmissions: (params) => api.get('/dashboard/submissions', { params }),
  getSubmissionDetail: (submissionId) => api.get(`/dashboard/submissions/${submissionId}`),
  deleteSubmission: (submissionId) => api.delete(`/dashboard/submissions/${submissionId}`),
  getDeadlines: (includePast = false) => api.get('/dashboard/deadlines', { params: { include_past: includePast } }),
  createDeadline: (data) => api.post('/dashboard/deadlines', data),
  updateDeadline: (deadlineId, data) => api.put(`/dashboard/deadlines/${deadlineId}`, data),
  deleteDeadline: (deadlineId) => api.delete(`/dashboard/deadlines/${deadlineId}`),
};

// Metadata API
export const metadataAPI = {
  analyzeSubmission: (submissionId) => api.post(`/metadata/analyze/${submissionId}`),
  getResult: (submissionId) => api.get(`/metadata/result/${submissionId}`),
};

// Insights API
export const insightsAPI = {
  analyzeSubmission: (submissionId) => api.post(`/insights/analyze/${submissionId}`),
  getTimeliness: (submissionId) => api.get(`/insights/timeliness/${submissionId}`),
  getContribution: (submissionId) => api.get(`/insights/contribution/${submissionId}`),
};

// NLP API
export const nlpAPI = {
  analyzeSubmission: (submissionId) => api.post(`/nlp/analyze/${submissionId}`),
  getReadability: (submissionId) => api.get(`/nlp/readability/${submissionId}`),
  getEntities: (submissionId) => api.get(`/nlp/entities/${submissionId}`),
};

// Reports API
export const reportsAPI = {
  exportPDF: (submissionIds) => api.post('/reports/export/pdf', { submission_ids: submissionIds }),
  exportCSV: (submissionIds) => api.post('/reports/export/csv', { submission_ids: submissionIds }),
  downloadExport: (exportId) => api.get(`/reports/download/${exportId}`, { responseType: 'blob' }),
  getExports: () => api.get('/reports/exports'),
};

export default api;
