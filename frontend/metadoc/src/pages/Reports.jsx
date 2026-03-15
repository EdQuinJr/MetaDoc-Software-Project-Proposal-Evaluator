import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Search,
    FileText,
    Hash,
    Calendar,
    ChevronRight,
    Trash2,
    CheckCircle,
    AlertTriangle,
    TrendingUp
} from 'lucide-react';
import { dashboardAPI } from '../services/api';
import '../styles/Reports.css';

const formatStudentId = (input) => {
    if (!input) return 'N/A';
    const digits = input.replace(/\D/g, '').slice(0, 9);
    if (digits.length <= 2) return digits;
    if (digits.length <= 6) return `${digits.slice(0, 2)}-${digits.slice(2)}`;
    return `${digits.slice(0, 2)}-${digits.slice(2, 6)}-${digits.slice(6, 9)}`;
};

const formatDateTime = (value) => {
    if (!value) return { date: '-', time: '-' };
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return { date: '-', time: '-' };
    return {
        date: date.toLocaleDateString('en-US'),
        time: date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
    };
};

const resolveSchoolYear = () => {
    // SY follows the active school year label based on current year (ex: 2026-2027).
    const currentYear = new Date().getFullYear();
    return `${currentYear}-${currentYear + 1}`;
};

const getStatusMeta = (status = '') => {
    const normalized = String(status || '').toLowerCase();
    if (normalized === 'late') {
        return { text: 'LATE', className: 'status-late', Icon: AlertTriangle };
    }
    return { text: 'ON TIME', className: 'status-ontime', Icon: CheckCircle };
};

const getDeliverableTitle = (submission, deadlineTitleMap) => {
    const directId = submission?.deadline_id;
    const normalizedId = directId !== undefined && directId !== null ? String(directId) : null;

    return (
        deadlineTitleMap.get(directId) ||
        (normalizedId ? deadlineTitleMap.get(normalizedId) : null) ||
        submission.deadline_title ||
        submission.title ||
        'Untitled Deliverable'
    );
};

const Reports = () => {
    const navigate = useNavigate();
    const [submissions, setSubmissions] = useState([]);
    const [deadlines, setDeadlines] = useState([]);
    const [students, setStudents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [sortOption, setSortOption] = useState('none');
    const [teamCodeFilter, setTeamCodeFilter] = useState('none');
    const [deliverableFilter, setDeliverableFilter] = useState('none');

    const deadlineTitleMap = useMemo(() => {
        const map = new Map();
        deadlines.forEach((deadline) => {
            const title = deadline.title || 'Untitled Deliverable';
            map.set(deadline.id, title);
            map.set(String(deadline.id), title);
        });
        return map;
    }, [deadlines]);

    const teamCodeOptions = useMemo(() => {
        const codes = students
            .map((student) => String(student.team_code || '').trim())
            .filter(Boolean);

        return [...new Set(codes)].sort((left, right) => left.localeCompare(right, undefined, { numeric: true }));
    }, [students]);

    const deliverableOptions = useMemo(() => {
        return [...deadlines]
            .map((deadline) => ({
                id: String(deadline.id),
                title: deadline.title || 'Untitled Deliverable',
            }))
            .sort((left, right) => left.title.localeCompare(right.title));
    }, [deadlines]);

    const fetchAllSubmissions = async () => {
        try {
            setLoading(true);
            const [submissionsResponse, deadlinesResponse, studentsResponse] = await Promise.all([
                dashboardAPI.getSubmissions({
                    page: 1,
                    per_page: 2000,
                }),
                dashboardAPI.getDeadlines(true),
                dashboardAPI.getDeadlineStudents(),
            ]);

            setSubmissions(submissionsResponse.data?.submissions || []);
            setDeadlines(deadlinesResponse.data?.deadlines || []);
            setStudents(studentsResponse.data?.students || []);
        } catch (error) {
            console.error('Failed to fetch submissions for reports:', error);
            setSubmissions([]);
            setDeadlines([]);
            setStudents([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAllSubmissions();
    }, []);

    const visibleRows = useMemo(() => {
        const term = searchTerm.trim().toLowerCase();
        let rows = [...submissions];

        if (term) {
            rows = rows.filter((submission) => {
                const deliverableTitle = getDeliverableTitle(submission, deadlineTitleMap);
                const filename = submission.filename || submission.original_filename || '';
                const studentId = submission.student_id || '';
                const studentName = submission.student_name || '';
                return (
                    deliverableTitle.toLowerCase().includes(term) ||
                    filename.toLowerCase().includes(term) ||
                    studentId.toLowerCase().includes(term) ||
                    studentName.toLowerCase().includes(term)
                );
            });
        }

        if (teamCodeFilter !== 'none') {
            rows = rows.filter((submission) => String(submission.team_code || '').trim() === teamCodeFilter);
        }

        if (deliverableFilter !== 'none') {
            rows = rows.filter((submission) => String(submission.deadline_id || '') === deliverableFilter);
        }

        if (sortOption === 'newest') {
            rows.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        } else if (sortOption === 'oldest') {
            rows.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
        } else if (sortOption === 'a_z') {
            rows.sort((a, b) => {
                const left = getDeliverableTitle(a, deadlineTitleMap).toLowerCase();
                const right = getDeliverableTitle(b, deadlineTitleMap).toLowerCase();
                return left.localeCompare(right);
            });
        }

        return rows;
    }, [submissions, searchTerm, sortOption, teamCodeFilter, deliverableFilter, deadlineTitleMap]);

    const handleDelete = async (submissionId) => {
        const confirmed = window.confirm('Delete this submitted file?');
        if (!confirmed) return;

        try {
            await dashboardAPI.deleteSubmission(submissionId);
            setSubmissions((prev) => prev.filter((item) => item.id !== submissionId));
        } catch (error) {
            console.error('Failed to delete submission:', error);
            alert('Unable to delete this submission. Please try again.');
        }
    };

    return (
        <div className="reports-page">
            <div className="reports-container">
                <header className="reports-header">
                    <div className="header-title">
                        <TrendingUp size={24} className="text-maroon" />
                        <h1>Reports</h1>
                    </div>
                </header>

                <p className="reports-description">
                    View all submitted files by deliverable title, track submission details, and manage report records in one place.
                </p>

                <div className="reports-toolbar">
                    <div className="search-input-wrapper">
                        <Search size={18} className="search-icon" />
                        <input
                            type="text"
                            className="search-input"
                            placeholder="Search title, student ID, student name..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>

                    <select
                        className="filter-select team-code-filter-select"
                        value={teamCodeFilter}
                        onChange={(e) => setTeamCodeFilter(e.target.value)}
                    >
                        <option value="none">Select Code</option>
                        {teamCodeOptions.map((teamCode) => (
                            <option key={teamCode} value={teamCode}>{teamCode}</option>
                        ))}
                    </select>

                    <select
                        className="filter-select deliverable-filter-select"
                        value={deliverableFilter}
                        onChange={(e) => setDeliverableFilter(e.target.value)}
                    >
                        <option value="none">Select Title</option>
                        {deliverableOptions.map((deliverable) => (
                            <option key={deliverable.id} value={deliverable.id}>{deliverable.title}</option>
                        ))}
                    </select>

                    <select
                        className="filter-select"
                        value={sortOption}
                        onChange={(e) => setSortOption(e.target.value)}
                    >
                        <option value="none">NONE</option>
                        <option value="newest">Newest</option>
                        <option value="oldest">Oldest</option>
                        <option value="a_z">A-Z (Title)</option>
                    </select>
                </div>

                <div className="table-container reports-table-wrap">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>File Name</th>
                                <th>Student ID</th>
                                <th>Student Name</th>
                                <th>Date Submitted</th>
                                <th>Last Modified</th>
                                <th>Course &amp; Year</th>
                                <th>Team Code</th>
                                <th>SY</th>
                                <th>Status</th>
                                <th className="text-right">Actions</th>
                            </tr>
                        </thead>

                        <tbody>
                            {loading && (
                                <tr>
                                    <td colSpan="11" className="empty-table-state">Loading submitted files...</td>
                                </tr>
                            )}

                            {!loading && visibleRows.length === 0 && (
                                <tr>
                                    <td colSpan="11" className="empty-table-state">No submitted files found.</td>
                                </tr>
                            )}

                            {!loading && visibleRows.map((submission) => {
                                const submitted = formatDateTime(submission.created_at);
                                const modified = formatDateTime(submission.last_modified || submission.updated_at || submission.created_at);
                                const status = getStatusMeta(submission.status);
                                const deliverableTitle = getDeliverableTitle(submission, deadlineTitleMap);
                                const filename = submission.filename || submission.original_filename || 'Untitled';

                                return (
                                    <tr key={submission.id}>
                                        <td>
                                            <span className="file-name" title={deliverableTitle}>{deliverableTitle}</span>
                                        </td>

                                        <td>
                                            <div className="file-info-cell">
                                                <span className="file-icon-mini"><FileText size={14} /></span>
                                                <span className="file-name" title={filename}>{filename}</span>
                                            </div>
                                        </td>

                                        <td>
                                            <span className="student-id-pill">
                                                <Hash size={12} className="icon-subtle" />
                                                {formatStudentId(submission.student_id || '')}
                                            </span>
                                        </td>

                                        <td>{submission.student_name || 'N/A'}</td>

                                        <td>
                                            <div className="date-cell">
                                                <span><Calendar size={12} className="icon-subtle" /> {submitted.date}</span>
                                                <span className="time-subtle">{submitted.time}</span>
                                            </div>
                                        </td>

                                        <td>
                                            <div className="date-cell">
                                                <span><Calendar size={12} className="icon-subtle" /> {modified.date}</span>
                                                <span className="time-subtle">{modified.time}</span>
                                            </div>
                                        </td>

                                        <td>{submission.course_year || 'N/A'}</td>
                                        <td>{submission.team_code || 'N/A'}</td>
                                        <td>{resolveSchoolYear()}</td>

                                        <td>
                                            <span className={`status-pill ${status.className}`}>
                                                <status.Icon size={12} />
                                                {status.text}
                                            </span>
                                        </td>

                                        <td className="actions-cell text-right">
                                            <button
                                                type="button"
                                                className="btn-icon btn-view"
                                                onClick={() => navigate(`/dashboard/submissions/${submission.id}`, { state: { from: '/dashboard/reports', fromState: {} } })}
                                                title="View Submission Details"
                                            >
                                                <ChevronRight size={16} />
                                            </button>
                                            <button
                                                type="button"
                                                className="btn-icon btn-delete-row"
                                                onClick={() => handleDelete(submission.id)}
                                                title="Delete Submission"
                                            >
                                                <Trash2 size={16} />
                                            </button>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>

                {!loading && (
                    <div className="reports-footnote">
                        Showing {visibleRows.length} submitted file{visibleRows.length === 1 ? '' : 's'}.
                    </div>
                )}
            </div>
        </div>
    );
};

export default Reports;
