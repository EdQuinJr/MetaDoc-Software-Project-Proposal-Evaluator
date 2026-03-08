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
    Trash2
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
                id: s.student_id,
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

    const handleToggleSelect = (studentId) => {
        setSelectedIds(prev =>
            prev.includes(studentId)
                ? prev.filter(id => id !== studentId)
                : [...prev, studentId]
        );
    };

    const handleBulkDelete = async () => {
        if (selectedIds.length === 0) return;

        if (!window.confirm(`Are you sure you want to delete ${selectedIds.length} selected student records?`)) {
            return;
        }

        try {
            setLoading(true);
            const errors = [];
            for (const studentId of selectedIds) {
                const student = classRows.find(r => r.id === studentId);
                if (student) {
                    try {
                        await dashboardAPI.deleteDeadlineStudent(student.deadlineId, student.id);
                    } catch (err) {
                        errors.push(student.id);
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

    const handleDeleteStudent = async (studentId, deadlineId) => {
        if (!window.confirm('Are you sure you want to delete this student record?')) {
            return;
        }

        try {
            setLoading(true);
            await dashboardAPI.deleteDeadlineStudent(deadlineId, studentId);
            fetchStudents();
        } catch (err) {
            console.error('Failed to delete student:', err);
            setError('Failed to delete student record.');
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
                                    <div className="bulk-actions fade-in" style={{ display: 'flex', alignItems: 'center' }}>
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
                            {selectedFolder && classRows.length > 0 && (
                                <span className="record-count">{classRows.length} Students</span>
                            )}
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
                                                        (row.id?.toLowerCase() || '').includes(searchStr) ||
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
                                                    <td className="font-mono">{row.id}</td>
                                                    <td className="font-bold">{row.lastName}</td>
                                                    <td>{row.firstName}</td>
                                                    <td>
                                                        <span className="text-blue-600 underline">{row.email}</span>
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

            {/* Hidden Input for Future Import Logic if needed */}
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
