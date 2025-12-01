import { useState, useEffect } from 'react';
import { dashboardAPI } from '../services/api';
import { Calendar, Plus, Trash2, Edit2, AlertCircle, CheckCircle } from 'lucide-react';
import './Deadlines.css';

const Deadlines = () => {
  const [deadlines, setDeadlines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingDeadline, setEditingDeadline] = useState(null);
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    deadline_datetime: '',
  });

  useEffect(() => {
    fetchDeadlines();
  }, []);

  const fetchDeadlines = async () => {
    try {
      setLoading(true);
      const response = await dashboardAPI.getDeadlines(false);
      setDeadlines(response.data.deadlines || []);
    } catch (err) {
      console.error('Failed to fetch deadlines:', err);
      setError('Failed to load deadlines');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingDeadline) {
        // Update existing deadline
        await dashboardAPI.updateDeadline(editingDeadline.id, formData);
      } else {
        // Create new deadline
        await dashboardAPI.createDeadline(formData);
      }
      
      setShowModal(false);
      setFormData({ title: '', description: '', deadline_datetime: '' });
      setEditingDeadline(null);
      fetchDeadlines();
    } catch (err) {
      console.error('Failed to save deadline:', err);
      alert('Failed to save deadline. Please try again.');
    }
  };

  const handleEdit = (deadline) => {
    setEditingDeadline(deadline);
    
    // Format datetime for input (local timezone)
    const dt = new Date(deadline.deadline_datetime);
    const year = dt.getFullYear();
    const month = String(dt.getMonth() + 1).padStart(2, '0');
    const day = String(dt.getDate()).padStart(2, '0');
    const hours = String(dt.getHours()).padStart(2, '0');
    const minutes = String(dt.getMinutes()).padStart(2, '0');
    const formattedDateTime = `${year}-${month}-${day}T${hours}:${minutes}`;
    
    setFormData({
      title: deadline.title,
      description: deadline.description || '',
      deadline_datetime: formattedDateTime,
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this deadline?')) return;
    
    try {
      await dashboardAPI.deleteDeadline(id);
      fetchDeadlines();
    } catch (err) {
      console.error('Failed to delete deadline:', err);
      alert('Failed to delete deadline. Please try again.');
    }
  };

  const handleNewDeadline = () => {
    setEditingDeadline(null);
    setFormData({ title: '', description: '', deadline_datetime: '' });
    setShowModal(true);
  };

  const getTimeRemaining = (deadlineDate) => {
    const now = new Date();
    const deadline = new Date(deadlineDate);
    const diff = deadline - now;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));

    if (diff < 0) return { text: 'Overdue', color: 'error' };
    if (days === 0 && hours < 24) return { text: `${hours}h remaining`, color: 'warning' };
    if (days === 0) return { text: 'Today', color: 'warning' };
    if (days === 1) return { text: 'Tomorrow', color: 'info' };
    return { text: `${days} days`, color: 'success' };
  };

  if (loading) {
    return (
      <div className="deadlines-loading">
        <div className="spinner"></div>
        <p>Loading deadlines...</p>
      </div>
    );
  }

  return (
    <div className="deadlines-page">
      <div className="deadlines-header">
        <div>
          <h1>Deadline Management</h1>
          <p className="deadlines-subtitle">Create and manage submission deadlines</p>
        </div>
        <button className="btn btn-primary" onClick={handleNewDeadline}>
          <Plus size={20} />
          New Deadline
        </button>
      </div>

      {error && (
        <div className="alert alert-error">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {deadlines.length === 0 ? (
        <div className="empty-state">
          <Calendar size={64} />
          <h3>No deadlines yet</h3>
          <p>Create your first deadline to start tracking submissions</p>
          <button className="btn btn-primary mt-lg" onClick={handleNewDeadline}>
            <Plus size={20} />
            Create Deadline
          </button>
        </div>
      ) : (
        <div className="deadlines-grid">
          {deadlines.map((deadline) => {
            const timeInfo = getTimeRemaining(deadline.deadline_datetime);
            return (
              <div key={deadline.id} className="deadline-card">
                <div className="deadline-card-header">
                  <div className="deadline-icon">
                    <Calendar size={24} />
                  </div>
                  <div className="deadline-actions">
                    <button
                      className="btn-icon"
                      onClick={() => handleEdit(deadline)}
                      title="Edit"
                    >
                      <Edit2 size={18} />
                    </button>
                    <button
                      className="btn-icon btn-icon-danger"
                      onClick={() => handleDelete(deadline.id)}
                      title="Delete"
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                </div>
                
                <div className="deadline-card-body">
                  <h3>{deadline.title}</h3>
                  {deadline.description && (
                    <p className="deadline-description">{deadline.description}</p>
                  )}
                  
                  <div className="deadline-meta">
                    <div className="deadline-date">
                      <Calendar size={16} />
                      <span>{new Date(deadline.deadline_datetime).toLocaleString()}</span>
                    </div>
                    <div className={`deadline-status status-${timeInfo.color}`}>
                      {timeInfo.text}
                    </div>
                  </div>
                  
                  <div className="deadline-stats">
                    <div className="stat-item">
                      <span className="stat-value">{deadline.submission_count || 0}</span>
                      <span className="stat-label">Submissions</span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingDeadline ? 'Edit Deadline' : 'Create New Deadline'}</h2>
              <button className="btn-close" onClick={() => setShowModal(false)}>
                ×
              </button>
            </div>
            
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="title">Title *</label>
                <input
                  type="text"
                  id="title"
                  className="form-control"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  required
                  placeholder="e.g., Final Project Submission"
                />
              </div>

              <div className="form-group">
                <label htmlFor="description">Description</label>
                <textarea
                  id="description"
                  className="form-control"
                  rows="3"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Optional description or instructions"
                />
              </div>

              <div className="form-group">
                <label htmlFor="deadline_datetime">Deadline Date & Time *</label>
                <input
                  type="datetime-local"
                  id="deadline_datetime"
                  className="form-control"
                  value={formData.deadline_datetime}
                  onChange={(e) => setFormData({ ...formData, deadline_datetime: e.target.value })}
                  required
                />
              </div>

              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowModal(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  {editingDeadline ? 'Update' : 'Create'} Deadline
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Deadlines;
