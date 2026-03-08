import React, { useState, useEffect, useRef } from 'react';
import {
    Users,
    FileUp,
    CheckCircle2,
    XCircle,
    Search,
    Folder as FolderIcon,
    AlertCircle,
    Loader2,
    ArrowUpDown,
    Trash2,
    Plus,
    Save,
    X
} from 'lucide-react';
import { dashboardAPI } from '../services/api';
import Card from '../components/common/Card/Card';
import Button from '../components/common/Button/Button';
import '../styles/ClassRecord.css';

const ClassRecord = () => {
    const [folders, setFolders] = useState([]);
    const [selectedFolder, setSelectedFolder] = useState('');
    const [loading, setLoading] = useState(false);
    const [fetchingFolders, setFetchingFolders] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [sortBy, setSortBy] = useState('name-asc');
    const [error, setError] = useState(null);
    const [selectedIds, setSelectedIds] = useState([]);

    // Modal state
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isEditing, setIsEditing] = useState(false);
    const [currentStudentId, setCurrentStudentId] = useState(null); // Database ID
    const [formData, setFormData] = useState({
        student_id: '',
        last_name: '',
        first_name: '',
        email: ''
    });

    const fileInputRef = useRef(null);

    // Student records from backend
    const [classRows, setClassRows] = useState([]);

    useEffect(() => {
        fetchFolders();
    }, []);

    // Fetch students when folder changes
    useEffect(() => {
        if (selectedFolder) {
            fetchStudents();
        } else {
            setClassRows([]);
            setSelectedIds([]);
        }
    }, [selectedFolder]);

    // Auto-clear error after 3 seconds
    useEffect(() => {
        if (error) {
            const timer = setTimeout(() => {
                setError(null);
            }, 3000);
            return () => clearTimeout(timer);
        }
    }, [error]);

    const fetchFolders = async () => {
        try {
            setFetchingFolders(true);
            const response = await dashboardAPI.getDeadlines();
            setFolders(response.data.deadlines || []);
        } catch (err) {
            console.error('Failed to fetch folders:', err);
        } finally {
            setFetchingFolders(false);
        }
    };

    const fetchStudents = async () => {
        try {
            setLoading(true);
            const response = await dashboardAPI.getDeadlineStudents(selectedFolder);
            // Map backend fields to frontend display fields
            const mapped = (response.data.students || []).map(s => ({
                id: s.id, // Database UUID
                studentId: formatStudentId(s.student_id), // Format for display
                lastName: s.last_name,
                firstName: s.first_name,
                email: s.email,
                status: s.status,
                registrationDate: s.registration_date,
                deadlineTitle: s.deadline_title,
                deadlineId: s.deadline_id
            }));
            setClassRows(mapped);
            setSelectedIds([]); // Reset selection on fetch
        } catch (err) {
            console.error('Failed to fetch students:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleImportClick = () => {
        fileInputRef.current.click();
    };

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = async (event) => {
            const text = event.target.result;
            const rows = text.split('\n');
            const headers = rows[0].toLowerCase().split(',');

            const idIdx = headers.findIndex(h => h.includes('id') || h.includes('number'));
            const lastIdx = headers.findIndex(h => h.includes('last') || h.includes('surname'));
            const firstIdx = headers.findIndex(h => h.includes('first') || h.includes('given'));
            const emailIdx = headers.findIndex(h => h.includes('email') || h.includes('mail'));

            if (idIdx === -1 || lastIdx === -1) {
                setError('CSV must contain ID and Last Name columns.');
                return;
            }

            const students = [];
            for (let i = 1; i < rows.length; i++) {
                const row = rows[i].split(',').map(s => s.trim());
                if (row.length < 2) continue;

                const studentId = row[idIdx];
                if (!studentId) continue;

                students.push({
                    student_id: studentId,
                    last_name: row[lastIdx] || '',
                    first_name: firstIdx !== -1 ? row[firstIdx] : '',
                    email: emailIdx !== -1 ? row[emailIdx] : ''
                });
            }

            try {
                setLoading(true);
                await dashboardAPI.importDeadlineStudents(selectedFolder, students);
                fetchStudents();
            } catch (err) {
                console.error('Import failed:', err);
                setError(err.response?.data?.error || 'Failed to import student record.');
            } finally {
                setLoading(false);
                e.target.value = ''; // Reset input
            }
        };
        reader.readAsText(file);
    };

    const handleToggleSelect = (id) => {
        setSelectedIds(prev =>
            prev.includes(id)
                ? prev.filter(i => i !== id)
                : [...prev, id]
        );
    };

    const formatStudentId = (input) => {
        if (!input) return '';
        // Remove all non-digits
        const digits = input.replace(/\D/g, '');
        
        // Pattern: XX-XXXX-XXX (total 9 digits)
        const limited = digits.slice(0, 9);
        
        let result = '';
        if (limited.length > 0) {
            result += limited.slice(0, 2);
            if (limited.length > 2) {
                result += '-' + limited.slice(2, 6);
                if (limited.length > 6) {
                    result += '-' + limited.slice(6, 9);
                }
            }
        }
        return result;
    };

    const handleRowChange = (id, field, value) => {
        const finalValue = field === 'studentId' ? formatStudentId(value) : value;
        setClassRows(prev => prev.map(row =>
            row.id === id ? { ...row, [field]: finalValue } : row
        ));
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            handleBulkSave();
        }
    };

    const handleBulkSave = async () => {
        if (selectedIds.length === 0) return;

        try {
            setLoading(true);
            const errors = [];
            for (const id of selectedIds) {
                const row = classRows.find(r => r.id === id);
                if (row) {
                    try {
                        const updateData = {
                            student_id: row.studentId,
                            last_name: row.lastName,
                            first_name: row.firstName,
                            email: row.email
                        };
                        await dashboardAPI.updateDeadlineStudent(row.deadlineId, row.id, updateData);
                    } catch (err) {
                        errors.push(row.studentId);
                    }
                }
            }

            if (errors.length > 0) {
                setError(`Failed to save some records: ${errors.length} errors occurred.`);
            } else {
                fetchStudents();
                setSelectedIds([]);
            }
        } catch (err) {
            console.error('Bulk save error:', err);
            setError('An error occurred during save.');
        } finally {
            setLoading(false);
        }
    };

    const handleBulkDelete = async () => {
        if (selectedIds.length === 0) return;

        if (!window.confirm(`Are you sure you want to delete ${selectedIds.length} selected student records?`)) {
            return;
        }

        try {
            setLoading(true);
            const errors = [];
            for (const id of selectedIds) {
                const student = classRows.find(r => r.id === id);
                if (student) {
                    try {
                        // Use database ID (UUID) for safer deletion
                        await dashboardAPI.deleteDeadlineStudent(student.deadlineId, student.id);
                    } catch (err) {
                        errors.push(student.studentId);
                    }
                }
            }

            if (errors.length > 0) {
                setError(`Failed to delete some records: ${errors.length} errors occurred.`);
            }

            fetchStudents();
            setSelectedIds([]);
        } catch (err) {
            console.error('Bulk delete error:', err);
            setError('An error occurred during bulk deletion.');
        } finally {
            setLoading(false);
        }
    };

    const handleOpenAddModal = () => {
        setIsEditing(false);
        setCurrentStudentId(null);
        setFormData({
            student_id: '',
            last_name: '',
            first_name: '',
            email: ''
        });
        setIsModalOpen(true);
    };

    const handleModalSubmit = async (e) => {
        e.preventDefault();
        if (!selectedFolder || selectedFolder === 'all') {
            setError('Please select a specific folder first.');
            return;
        }

        try {
            setLoading(true);
            await dashboardAPI.addDeadlineStudent(selectedFolder, formData);
            setIsModalOpen(false);
            fetchStudents();
        } catch (err) {
            console.error('Operation failed:', err);
            setError(err.response?.data?.error || 'Failed to process student record.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="class-record-page fade-in">
            <div className="page-container">
                <div className="class-record-header">
                    <div className="header-title-group">
                        <Users size={24} className="text-maroon" />
                        <h1>Class Record</h1>
                    </div>
                </div>

                <div className="main-content">
                    {error && (
                        <div className="import-error-banner">
                            <AlertCircle size={20} />
                            <span>{error}</span>
                            <button className="error-close-btn" onClick={() => setError(null)}>×</button>
                        </div>
                    )}
                    <Card className="table-card">
                        <div className="table-header-row">
                            <div className="table-controls">
                                <div className="folder-select-container">
                                    {fetchingFolders ? (
                                        <Loader2 size={18} className="animate-spin text-gray-400" />
                                    ) : (
                                        <select
                                            className="folder-dropdown-inline"
                                            value={selectedFolder}
                                            onChange={(e) => setSelectedFolder(e.target.value)}
                                        >
                                            <option value="">-- Choose a Folder --</option>
                                            <option value="all" className="font-bold text-maroon">ALL</option>
                                            {folders.map(folder => (
                                                <option key={folder.id} value={folder.id}>
                                                    {folder.title}
                                                </option>
                                            ))}
                                        </select>
                                    )}
                                </div>

                                <div className="sort-container">
                                    <div className="search-box sort-box">
                                        <ArrowUpDown size={18} />
                                        <select
                                            className="sort-dropdown"
                                            value={sortBy}
                                            onChange={(e) => setSortBy(e.target.value)}
                                            disabled={!selectedFolder}
                                        >
                                            <option value="name-asc">A-Z (Name)</option>
                                            <option value="name-desc">Z-A (Name)</option>
                                            <option value="date-desc">Latest Registered</option>
                                            <option value="date-asc">Oldest Registered</option>
                                        </select>
                                    </div>
                                </div>

                                <div className="search-box">
                                    <Search size={18} />
                                    <input
                                        type="text"
                                        placeholder="Search by ID, Name or Email..."
                                        value={searchTerm}
                                        onChange={(e) => setSearchTerm(e.target.value)}
                                        disabled={!selectedFolder}
                                    />
                                </div>

                                {selectedIds.length > 0 && (
                                    <div className="bulk-actions fade-in" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        <button
                                            onClick={handleBulkSave}
                                            style={{
                                                color: '#000000',
                                                background: 'none',
                                                border: 'none',
                                                padding: '4px',
                                                cursor: 'pointer',
                                                display: 'flex',
                                                alignItems: 'center',
                                                transition: 'none'
                                            }}
                                            title="Save Changes"
                                            disabled={loading}
                                        >
                                            <Save size={16} />
                                            <span style={{ marginLeft: '4px', fontSize: '0.85rem', fontWeight: '500' }}>Save</span>
                                        </button>
                                        <button
                                            onClick={handleBulkDelete}
                                            style={{
                                                color: '#000000',
                                                background: 'none',
                                                border: 'none',
                                                padding: '4px',
                                                cursor: 'pointer',
                                                display: 'flex',
                                                alignItems: 'center',
                                                transition: 'none'
                                            }}
                                            title={`Delete Selected (${selectedIds.length})`}
                                            disabled={loading}
                                        >
                                            <Trash2 size={16} />
                                            <span style={{ marginLeft: '4px', fontSize: '0.85rem', fontWeight: '500' }}>Delete</span>
                                        </button>
                                    </div>
                                )}
                            </div>

                            <div className="table-actions">
                                {selectedFolder && selectedFolder !== 'all' && (
                                    <button
                                        className="add-student-btn-maroon"
                                        onClick={handleOpenAddModal}
                                        title="Add Student Manually"
                                    >
                                        <Plus size={16} />
                                    </button>
                                )}
                                {selectedFolder && classRows.length > 0 && (
                                    <span className="record-count">{classRows.length} Students</span>
                                )}
                            </div>
                        </div>

                        <div className="table-container">
                            {selectedFolder ? (
                                <table className="record-table">
                                    <thead>
                                        <tr>
                                            <th style={{ width: '40px' }}>
                                                <input
                                                    type="checkbox"
                                                    checked={classRows.length > 0 && selectedIds.length === classRows.length}
                                                    onChange={() => {
                                                        if (selectedIds.length === classRows.length) {
                                                            setSelectedIds([]);
                                                        } else {
                                                            setSelectedIds(classRows.map(r => r.id));
                                                        }
                                                    }}
                                                    className="row-checkbox"
                                                />
                                            </th>
                                            {selectedFolder === 'all' && <th>TITLE</th>}
                                            <th>ID Number</th>
                                            <th>Last Name</th>
                                            <th>First Name</th>
                                            <th>Email Address</th>
                                            <th>Date Registered</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {(() => {
                                            const filteredRows = classRows
                                                .filter(row => {
                                                    const searchStr = searchTerm.toLowerCase();
                                                    return (
                                                        (row.studentId?.toLowerCase() || '').includes(searchStr) ||
                                                        (row.lastName?.toLowerCase() || '').includes(searchStr) ||
                                                        (row.firstName?.toLowerCase() || '').includes(searchStr) ||
                                                        (row.email?.toLowerCase() || '').includes(searchStr)
                                                    );
                                                })
                                                .sort((a, b) => {
                                                    if (sortBy === 'name-asc') {
                                                        const nameA = `${a.lastName} ${a.firstName}`.toLowerCase();
                                                        const nameB = `${b.lastName} ${b.firstName}`.toLowerCase();
                                                        return nameA.localeCompare(nameB);
                                                    }
                                                    if (sortBy === 'name-desc') {
                                                        const nameA = `${a.lastName} ${a.firstName}`.toLowerCase();
                                                        const nameB = `${b.lastName} ${b.firstName}`.toLowerCase();
                                                        return nameB.localeCompare(nameA);
                                                    }
                                                    if (sortBy === 'date-desc') {
                                                        const dateA = a.registrationDate ? new Date(a.registrationDate) : new Date(0);
                                                        const dateB = b.registrationDate ? new Date(b.registrationDate) : new Date(0);
                                                        return dateB - dateA;
                                                    }
                                                    if (sortBy === 'date-asc') {
                                                        const dateA = a.registrationDate ? new Date(a.registrationDate) : new Date(0);
                                                        const dateB = b.registrationDate ? new Date(b.registrationDate) : new Date(0);
                                                        return dateA - dateB;
                                                    }
                                                    return 0;
                                                });

                                            if (classRows.length === 0) {
                                                const colSpan = selectedFolder === 'all' ? 8 : 7;
                                                return (
                                                    <tr>
                                                        <td colSpan={colSpan} className="no-padding">
                                                            <div className="empty-state-dashed-inline">
                                                                <Users size={48} className="empty-icon-gray" />
                                                                <h3>No Student Records</h3>
                                                                {selectedFolder === 'all' ? (
                                                                    <p>Please select a specific folder to import or manage students.</p>
                                                                ) : (
                                                                    <>
                                                                        <p>Import a class record to start managing student registrations.</p>
                                                                        <Button
                                                                            onClick={handleImportClick}
                                                                            variant="primary"
                                                                            size="small"
                                                                            icon={FileUp}
                                                                            disabled={loading}
                                                                        >
                                                                            {loading ? 'Importing...' : 'Import Class Record'}
                                                                        </Button>
                                                                    </>
                                                                )}
                                                            </div>
                                                        </td>
                                                    </tr>
                                                );
                                            }

                                            if (filteredRows.length === 0) {
                                                const colSpan = selectedFolder === 'all' ? 8 : 7;
                                                return (
                                                    <tr>
                                                        <td colSpan={colSpan} className="search-no-results">
                                                            <div className="no-match-message">
                                                                <Search size={32} className="opacity-20" />
                                                                <p>No student records match "<strong>{searchTerm}</strong>"</p>
                                                                <Button
                                                                    variant="ghost"
                                                                    size="small"
                                                                    onClick={() => setSearchTerm('')}
                                                                >
                                                                    Clear Search
                                                                </Button>
                                                            </div>
                                                        </td>
                                                    </tr>
                                                );
                                            }

                                            return filteredRows.map((row, index) => (
                                                <tr key={index} style={{ backgroundColor: selectedIds.includes(row.id) ? '#fffaf0' : 'inherit' }}>
                                                    <td>
                                                        <input
                                                            type="checkbox"
                                                            checked={selectedIds.includes(row.id)}
                                                            onChange={() => handleToggleSelect(row.id)}
                                                            className="row-checkbox"
                                                        />
                                                    </td>
                                                    {selectedFolder === 'all' && (
                                                        <td className="font-bold text-maroon text-xs whitespace-nowrap">
                                                            {row.deadlineTitle}
                                                        </td>
                                                    )}
                                                    <td className="font-mono">
                                                        {selectedIds.includes(row.id) ? (
                                                            <input
                                                                className="inline-edit-input"
                                                                value={row.studentId}
                                                                onChange={(e) => handleRowChange(row.id, 'studentId', e.target.value)}
                                                                onKeyDown={handleKeyPress}
                                                            />
                                                        ) : row.studentId}
                                                    </td>
                                                    <td className="font-bold">
                                                        {selectedIds.includes(row.id) ? (
                                                            <input
                                                                className="inline-edit-input font-bold"
                                                                value={row.lastName}
                                                                onChange={(e) => handleRowChange(row.id, 'lastName', e.target.value)}
                                                                onKeyDown={handleKeyPress}
                                                            />
                                                        ) : row.lastName}
                                                    </td>
                                                    <td>
                                                        {selectedIds.includes(row.id) ? (
                                                            <input
                                                                className="inline-edit-input"
                                                                value={row.firstName}
                                                                onChange={(e) => handleRowChange(row.id, 'firstName', e.target.value)}
                                                                onKeyDown={handleKeyPress}
                                                            />
                                                        ) : row.firstName}
                                                    </td>
                                                    <td>
                                                        {selectedIds.includes(row.id) ? (
                                                            <input
                                                                className="inline-edit-input text-blue-600"
                                                                value={row.email}
                                                                onChange={(e) => handleRowChange(row.id, 'email', e.target.value)}
                                                                onKeyDown={handleKeyPress}
                                                            />
                                                        ) : (
                                                            <span className="text-blue-600 underline">{row.email}</span>
                                                        )}
                                                    </td>
                                                    <td>
                                                        {row.status === 'Registered' ? (
                                                            <span className="text-gray-500">{row.registrationDate}</span>
                                                        ) : (
                                                            <span className="text-gray-300">---</span>
                                                        )}
                                                    </td>
                                                    <td>
                                                        <span className={`status-tag ${row.status.toLowerCase()}`}>
                                                            {row.status === 'Registered' ? <CheckCircle2 size={12} /> : <XCircle size={12} />}
                                                            {row.status}
                                                        </span>
                                                    </td>
                                                </tr>
                                            ));
                                        })()}
                                    </tbody>
                                </table>
                            ) : (
                                <div className="no-selection-state">
                                    <FolderIcon size={64} className="opacity-10" />
                                    <p>Select a folder to view student records</p>
                                </div>
                            )}
                        </div>
                    </Card>
                </div>
            </div>

            {/* Manual Student Add/Edit Modal */}
            {isModalOpen && (
                <div className="modal-overlay">
                    <div className="modal-content student-modal">
                        <div className="modal-header">
                            <h2>{isEditing ? 'Edit Student Record' : 'Add New Student'}</h2>
                            <button className="modal-close" onClick={() => setIsModalOpen(false)}>
                                <X size={20} />
                            </button>
                        </div>
                        <form onSubmit={handleModalSubmit}>
                            <div className="form-group">
                                <label>Student ID Number</label>
                                <input
                                    type="text"
                                    required
                                    placeholder="22-1686-452"
                                    value={formData.student_id}
                                    onChange={(e) => setFormData({ ...formData, student_id: formatStudentId(e.target.value) })}
                                />
                            </div>
                            <div className="form-row">
                                <div className="form-group">
                                    <label>Last Name</label>
                                    <input
                                        type="text"
                                        required
                                        placeholder="Surname"
                                        value={formData.last_name}
                                        onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                                    />
                                </div>
                                <div className="form-group">
                                    <label>First Name</label>
                                    <input
                                        type="text"
                                        required
                                        placeholder="Given Name"
                                        value={formData.first_name}
                                        onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                                    />
                                </div>
                            </div>
                            <div className="form-group">
                                <label>Email Address (Gmail Preferred)</label>
                                <input
                                    type="email"
                                    placeholder="student@gmail.com"
                                    value={formData.email}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                />
                                <p className="form-hint">Used for matching document activity.</p>
                            </div>
                            <div className="modal-footer">
                                <Button
                                    type="button"
                                    variant="ghost"
                                    onClick={() => setIsModalOpen(false)}
                                    disabled={loading}
                                >
                                    Cancel
                                </Button>
                                <Button
                                    type="submit"
                                    variant="primary"
                                    disabled={loading}
                                >
                                    {loading ? 'Processing...' : (isEditing ? 'Update Record' : 'Add Student')}
                                </Button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            <input
                type="file"
                ref={fileInputRef}
                className="hidden"
                accept=".xlsx, .xls, .csv"
                onChange={handleFileChange}
            />
        </div>
    );
};

export default ClassRecord;
