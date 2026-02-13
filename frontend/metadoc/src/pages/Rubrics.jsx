import React, { useState, useEffect } from 'react';
import { rubricAPI } from '../services/api';
import { Plus, Edit2, Trash2, BookOpen, AlertCircle } from 'lucide-react';
import '../styles/Rubrics.css';

const Rubrics = () => {
    const [rubrics, setRubrics] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingRubric, setEditingRubric] = useState(null);
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [deleteTarget, setDeleteTarget] = useState(null);

    // Form state
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [criteria, setCriteria] = useState([{ name: '', description: '' }]);

    const loadTemplate = () => {
        setTitle('Software Project Proposal Evaluation');
        setDescription('Standard criteria for evaluating software engineering capstone proposals.');
        setCriteria([
            { name: 'Problem Statement', description: 'Clearly defined problem with evidence of significance and relevance.' },
            { name: 'Proposed Solution', description: 'Feasibility, innovation, and technical soundness of the proposed solution.' },
            { name: 'Technical Stack', description: 'Appropriateness of chosen technologies and tools.' },
            { name: 'Methodology', description: 'Clarity of the development process (e.g., Agile, Waterfall) and phases.' },
            { name: 'Documentation Quality', description: 'Grammar, structure, formatting, and adherence to guidelines.' }
        ]);
    };

    useEffect(() => {
        fetchRubrics();
    }, []);

    const fetchRubrics = async () => {
        try {
            setLoading(true);
            const response = await rubricAPI.getRubrics();
            setRubrics(response.data.rubrics || []);
        } catch (err) {
            setError('Failed to load rubrics');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleOpenModal = (rubric = null) => {
        if (rubric) {
            setEditingRubric(rubric);
            setTitle(rubric.title);
            setDescription(rubric.description || '');
            setCriteria(rubric.criteria || []);
        } else {
            setEditingRubric(null);
            setTitle('');
            setDescription('');
            setCriteria([{ name: '', description: '' }]);
        }
        setIsModalOpen(true);
    };

    const handleCloseModal = () => {
        setIsModalOpen(false);
        setError(null);
    };

    const handleDeleteClick = (rubric) => {
        setDeleteTarget(rubric);
        setShowDeleteModal(true);
    };

    const handleDeleteConfirm = async () => {
        if (!deleteTarget) return;

        try {
            await rubricAPI.deleteRubric(deleteTarget.id);
            setRubrics(rubrics.filter(r => r.id !== deleteTarget.id));
            setShowDeleteModal(false);
            setDeleteTarget(null);
        } catch (err) {
            console.error('Failed to delete rubric:', err);
            setError('Failed to delete rubric');
        }
    };

    const handleDeleteCancel = () => {
        setShowDeleteModal(false);
        setDeleteTarget(null);
    };

    const handleAddCriterion = () => {
        setCriteria([...criteria, { name: '', description: '' }]);
    };

    const handleRemoveCriterion = (index) => {
        const newCriteria = [...criteria];
        newCriteria.splice(index, 1);
        setCriteria(newCriteria);
    };

    const handleCriterionChange = (index, field, value) => {
        const newCriteria = [...criteria];
        newCriteria[index][field] = value;
        setCriteria(newCriteria);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!title) {
            alert('Title is required');
            return;
        }
        if (criteria.some(c => !c.name)) {
            alert('All criteria must have a name');
            return;
        }

        const payload = {
            title,
            description,
            criteria
        };

        try {
            if (editingRubric) {
                await rubricAPI.updateRubric(editingRubric.id, payload);
            } else {
                await rubricAPI.createRubric(payload);
            }
            handleCloseModal();
            fetchRubrics();
        } catch (err) {
            alert('Failed to save rubric');
            console.error(err);
        }
    };

    return (
        <div className="rubrics-page">
            <div className="rubrics-header">
                <div>
                    <h1>Rubric Management</h1>
                    <p className="rubrics-subtitle">Define criteria for AI-assisted evaluation</p>
                </div>
                <button
                    onClick={() => handleOpenModal()}
                    className="btn btn-primary"
                >
                    <Plus size={20} />
                    Create Rubric
                </button>
            </div>

            {loading ? (
                <div className="flex justify-center py-12">
                    <div className="spinner"></div>
                </div>
            ) : error ? (
                <div className="alert alert-error">
                    <AlertCircle size={20} />
                    <span>{error}</span>
                </div>
            ) : rubrics.length === 0 ? (
                <div className="empty-state">
                    <BookOpen size={64} style={{ color: '#E5E7EB' }} />
                    <h3>No Rubrics Found</h3>
                    <p>Create your first rubric to start standardizing your evaluations.</p>
                </div>
            ) : (
                <div className="rubrics-grid">
                    {rubrics.map((rubric) => (
                        <div key={rubric.id} className="rubric-card">
                            <div className="rubric-card-header">
                                <div className="rubric-title-group">
                                    <h3 title={rubric.title}>{rubric.title}</h3>
                                    <p className="rubric-description">
                                        {rubric.description || 'No description provided.'}
                                    </p>
                                </div>
                                <div className="flex gap-1">
                                    <button
                                        onClick={() => handleOpenModal(rubric)}
                                        className="btn-edit-rubric"
                                        title="Edit Rubric"
                                    >
                                        <Edit2 size={18} />
                                    </button>
                                    <button
                                        onClick={() => handleDeleteClick(rubric)}
                                        className="btn-edit-rubric"
                                        title="Delete Rubric"
                                        style={{ color: 'rgba(255, 255, 255, 0.7)' }}
                                    >
                                        <Trash2 size={18} />
                                    </button>
                                </div>
                            </div>

                            <div className="rubric-card-body">
                                <div className="criteria-preview">
                                    <p className="criteria-preview-title">Criteria Preview</p>
                                    <div className="criteria-list">
                                        {rubric.criteria.slice(0, 3).map((c, idx) => (
                                            <div key={idx} className="criterion-item">
                                                <span className="truncate w-full" title={c.description}>{c.name}</span>
                                            </div>
                                        ))}
                                        {rubric.criteria.length > 3 && (
                                            <p className="text-xs text-gray-400 italic mt-1 pl-1">
                                                + {rubric.criteria.length - 3} more criteria
                                            </p>
                                        )}
                                    </div>
                                </div>
                            </div>

                            <div className="rubric-card-footer">
                                <span>Created {new Date(rubric.created_at).toLocaleDateString()}</span>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Modal */}
            {isModalOpen && (
                <div className="modal-overlay">
                    <div className="modal-content">
                        <div className="modal-header">
                            <h2>{editingRubric ? 'Edit Rubric' : 'Create New Rubric'}</h2>
                            <button onClick={handleCloseModal} className="btn-close">
                                <span style={{ fontSize: '24px' }}>&times;</span>
                            </button>
                        </div>

                        <form onSubmit={handleSubmit}>
                            {/* Template Button */}
                            {!editingRubric && (
                                <div className="bg-blue-50 p-4 rounded-lg mb-6 flex justify-between items-center border border-blue-100">
                                    <div>
                                        <h4 className="font-semibold text-blue-900">Need a starting point?</h4>
                                        <p className="text-sm text-blue-700">Load a standard software proposal evaluation template.</p>
                                    </div>
                                    <button
                                        type="button"
                                        onClick={loadTemplate}
                                        className="text-sm bg-white border border-blue-200 text-blue-600 px-3 py-1.5 rounded hover:bg-blue-50 transition-colors font-medium shadow-sm"
                                    >
                                        Load Template
                                    </button>
                                </div>
                            )}

                            {/* Basic Info */}
                            <div className="space-y-4 mb-6">
                                <div className="form-group">
                                    <label>Rubric Title *</label>
                                    <input
                                        type="text"
                                        value={title}
                                        onChange={(e) => setTitle(e.target.value)}
                                        className="form-control"
                                        placeholder="e.g. Capstone Proposal Evaluation"
                                        required
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Description</label>
                                    <textarea
                                        value={description}
                                        onChange={(e) => setDescription(e.target.value)}
                                        className="form-control"
                                        placeholder="Briefly describe what this rubric evaluates..."
                                        rows="2"
                                    />
                                </div>
                            </div>

                            {/* Criteria Builder */}
                            <div>
                                <div className="flex justify-between items-center mb-4">
                                    <label className="text-sm font-bold text-gray-700 uppercase">Evaluation Criteria</label>
                                    <button
                                        type="button"
                                        onClick={handleAddCriterion}
                                        className="add-criterion-btn"
                                    >
                                        <Plus size={16} /> Add Criterion
                                    </button>
                                </div>

                                <div className="space-y-4 max-h-[40vh] overflow-y-auto pr-2">
                                    {criteria.map((criterion, idx) => (
                                        <div key={idx} className="criteria-input-group">
                                            <button
                                                type="button"
                                                onClick={() => handleRemoveCriterion(idx)}
                                                className="btn-remove-criterion"
                                                title="Remove Criterion"
                                            >
                                                <Trash2 size={16} />
                                            </button>
                                            <div className="grid grid-cols-1 gap-4">
                                                <div className="w-full">
                                                    <input
                                                        type="text"
                                                        value={criterion.name}
                                                        onChange={(e) => handleCriterionChange(idx, 'name', e.target.value)}
                                                        placeholder="Criterion Name (e.g. Clarity)"
                                                        className="form-control mb-2"
                                                        style={{ fontWeight: '500' }}
                                                        required
                                                    />
                                                    <textarea
                                                        value={criterion.description}
                                                        onChange={(e) => handleCriterionChange(idx, 'description', e.target.value)}
                                                        placeholder="Description of what to look for..."
                                                        className="form-control text-sm"
                                                        rows="2"
                                                    />
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div className="modal-footer">
                                <button
                                    type="button"
                                    onClick={handleCloseModal}
                                    className="btn btn-secondary"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="btn btn-primary"
                                >
                                    Save Rubric
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Delete Confirmation Modal */}
            {showDeleteModal && deleteTarget && (
                <div className="modal-overlay" onClick={handleDeleteCancel}>
                    <div className="modal-content delete-modal" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <div className="delete-icon">
                                <AlertCircle size={20} />
                            </div>
                            <h2>Delete Rubric</h2>
                        </div>

                        <div className="modal-body">
                            <p>Are you sure you want to delete <strong>"{deleteTarget.title}"</strong>?</p>
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

export default Rubrics;
