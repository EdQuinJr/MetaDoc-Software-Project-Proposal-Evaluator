import { useState, useEffect } from 'react';
import { reportsAPI, dashboardAPI } from '../services/api';
import { FileText, Download, TrendingUp, Loader2, PieChart as PieChartIcon, CheckCircle, AlertCircle, Clock } from 'lucide-react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import '../styles/Reports.css';

const Reports = () => {
    const [submissions, setSubmissions] = useState([]);
    const [statusData, setStatusData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [exporting, setExporting] = useState(false);

    // Pagination / Limits
    const [total, setTotal] = useState(0);

    // Chart Colors
    const COLORS = {
        'completed': '#10b981', // emerald-500
        'pending': '#f59e0b',   // amber-500
        'processing': '#3b82f6', // blue-500
        'failed': '#ef4444',    // red-500
        'warning': '#f97316'    // orange-500
    };

    const DEFAULT_COLOR = '#e5e7eb'; // gray-200

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            setLoading(true);
            const submissionsRes = await dashboardAPI.getSubmissions({ per_page: 100, sort_by: 'created_at', sort_order: 'desc' });

            const subs = submissionsRes.data.submissions || [];
            setSubmissions(subs);
            setTotal(submissionsRes.data.total || 0);

            // Process Data for Pie Chart
            const statusCounts = {};
            subs.forEach(sub => {
                const status = sub.status || 'unknown';
                statusCounts[status] = (statusCounts[status] || 0) + 1;
            });

            const processedStatusData = Object.keys(statusCounts).map(status => ({
                name: status.charAt(0).toUpperCase() + status.slice(1),
                value: statusCounts[status],
                key: status
            }));

            if (processedStatusData.length === 0) {
                processedStatusData.push({ name: 'No Data', value: 1, key: 'default' });
            }

            setStatusData(processedStatusData);

        } catch (err) {
            console.error('Failed to load reports:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleExportCSV = async () => {
        if (exporting) return;
        const confirmExport = window.confirm("Generate and download full CSV report?");
        if (!confirmExport) return;

        try {
            setExporting(true);
            const response = await reportsAPI.exportCSV({ filters: {} });

            if (response.data?.export_id) {
                const blobRes = await reportsAPI.downloadExport(response.data.export_id);
                const url = window.URL.createObjectURL(new Blob([blobRes.data]));
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute('download', response.data.filename || 'Full_Analysis_Report.csv');
                document.body.appendChild(link);
                link.click();
                link.remove();
                window.URL.revokeObjectURL(url);
            } else {
                alert("Export failed. Please try again.");
            }
        } catch (err) {
            console.error(err);
            alert("Export encountered an error.");
        } finally {
            setExporting(false);
        }
    };

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[400px] text-gray-500">
                <Loader2 size={32} className="animate-spin mb-3 text-indigo-600" />
                <p>Loading analytics data...</p>
            </div>
        );
    }

    // Helper to get count by key safely
    const getCount = (key) => statusData.find(d => d.key === key)?.value || 0;

    return (
        <div className="reports-page p-6 max-w-[1400px] mx-auto">
            {/* Header - Compact */}
            <header className="flex flex-row justify-between items-center mb-6">
                <div>
                    <h1 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                        <TrendingUp size={20} className="text-indigo-600" />
                        Analysis Reports
                    </h1>
                </div>
                <button
                    className="btn-export btn-primary-action text-sm px-3 py-1.5"
                    onClick={handleExportCSV}
                    disabled={exporting}
                >
                    {exporting ? <Loader2 size={14} className="animate-spin" /> : <Download size={14} />}
                    Export CSV
                </button>
            </header>

            {/* Top Section: Split Layout (Chart Left, Stats Right) */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6 h-full">

                {/* 1. Status Chart Card */}
                <div className="report-card p-4 lg:col-span-1 flex flex-col items-center justify-center relative">
                    <h3 className="text-sm font-semibold text-gray-700 w-full mb-2 flex items-center gap-2">
                        <PieChartIcon size={16} /> Status Distribution
                    </h3>
                    <div style={{ width: '100%', height: 180 }}>
                        <ResponsiveContainer>
                            <PieChart>
                                <Pie
                                    data={statusData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={50}
                                    outerRadius={70}
                                    paddingAngle={5}
                                    dataKey="value"
                                >
                                    {statusData.map((entry, index) => (
                                        <Cell
                                            key={`cell-${index}`}
                                            fill={COLORS[entry.key] || DEFAULT_COLOR}
                                            stroke="none"
                                        />
                                    ))}
                                </Pie>
                                <Tooltip
                                    contentStyle={{ borderRadius: '8px', border: 'none', fontSize: '12px' }}
                                />
                                <Legend
                                    layout="vertical"
                                    verticalAlign="middle"
                                    align="right"
                                    iconSize={8}
                                    wrapperStyle={{ fontSize: '11px' }}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* 2. Key Metrics Grid (Compact) */}
                <div className="lg:col-span-2 grid grid-cols-1 sm:grid-cols-3 gap-4">
                    {/* Stat Class 1: Total */}
                    <div className="report-card p-4 flex flex-col justify-between border-l-4 border-l-indigo-500">
                        <div className="text-gray-500 text-xs uppercase tracking-wider font-semibold mb-1">Total Submissions</div>
                        <div className="flex items-end justify-between">
                            <span className="text-3xl font-bold text-gray-800">{total}</span>
                            <FileText size={20} className="text-indigo-200 mb-1" />
                        </div>
                    </div>

                    {/* Stat Class 2: Completed */}
                    <div className="report-card p-4 flex flex-col justify-between border-l-4 border-l-emerald-500">
                        <div className="text-gray-500 text-xs uppercase tracking-wider font-semibold mb-1">Analyzed</div>
                        <div className="flex items-end justify-between">
                            <span className="text-3xl font-bold text-gray-800">{getCount('completed')}</span>
                            <CheckCircle size={20} className="text-emerald-200 mb-1" />
                        </div>
                    </div>

                    {/* Stat Class 3: Issues/Pending */}
                    <div className="report-card p-4 flex flex-col justify-between border-l-4 border-l-amber-500">
                        <div className="text-gray-500 text-xs uppercase tracking-wider font-semibold mb-1">Pending / Issues</div>
                        <div className="flex items-end justify-between">
                            <span className="text-3xl font-bold text-gray-800">
                                {getCount('pending') + getCount('failed')}
                            </span>
                            <div className="flex gap-1 mb-1">
                                <Clock size={16} className="text-amber-300" />
                                <AlertCircle size={16} className="text-red-300" />
                            </div>
                        </div>
                    </div>

                    {/* Description / Filler to fill grid if needed, or make row 2 full width stats */}
                    {/* Let's make a wide summary bar below metrics if space allows, or keep it compact above */}
                </div>
            </div>

            {/* Tabular Data Section - Dense Mode */}
            <div className="report-card overflow-hidden">
                <div className="px-5 py-3 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
                    <h3 className="text-sm font-semibold text-gray-800">Detailed Records</h3>
                    <span className="text-xs text-gray-500">
                        {submissions.length} Records
                    </span>
                </div>

                <div className="report-table-container">
                    <table className="report-table text-sm">
                        <thead>
                            <tr className="bg-gray-50 text-left">
                                <th className="py-2 px-4 font-medium text-gray-600 w-1/4">Student</th>
                                <th className="py-2 px-4 font-medium text-gray-600 w-1/4">File</th>
                                <th className="py-2 px-4 font-medium text-gray-600">Date</th>
                                <th className="py-2 px-4 font-medium text-gray-600">Status</th>
                                <th className="py-2 px-4 font-medium text-gray-600">Feedback Summary</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {submissions.length === 0 ? (
                                <tr>
                                    <td colSpan="5" className="text-center py-8 text-gray-500 text-sm">
                                        No recent submissions found.
                                    </td>
                                </tr>
                            ) : (
                                submissions.map(sub => (
                                    <tr key={sub.id} className="hover:bg-gray-50 transition-colors">
                                        <td className="py-2 px-4">
                                            <div className="font-medium text-gray-900">{sub.student_name || 'Unknown'}</div>
                                            <div className="text-xs text-gray-400">{sub.student_id}</div>
                                        </td>
                                        <td className="py-2 px-4">
                                            <div className="flex items-center gap-2 max-w-[200px]" title={sub.original_filename}>
                                                <FileText size={14} className="text-indigo-400 flex-shrink-0" />
                                                <span className="truncate text-gray-700">{sub.original_filename}</span>
                                            </div>
                                        </td>
                                        <td className="py-2 px-4 text-gray-500 text-xs">
                                            {new Date(sub.created_at).toLocaleDateString()}
                                        </td>
                                        <td className="py-2 px-4">
                                            <span className={`status-badge ${sub.status} text-xs py-0.5 px-2`}>
                                                {sub.status}
                                            </span>
                                        </td>
                                        <td className="py-2 px-4">
                                            {sub.analysis_summary?.ai_summary ? (
                                                <div className="group relative">
                                                    <p className="text-gray-600 truncate max-w-[250px] cursor-help">
                                                        {sub.analysis_summary.ai_summary}
                                                    </p>
                                                    {/* Tooltip */}
                                                    <div className="absolute right-0 bottom-full mb-1 w-64 p-2 bg-slate-800 text-white text-xs rounded shadow-lg opacity-0 group-hover:opacity-100 pointer-events-none z-50">
                                                        {sub.analysis_summary.ai_summary}
                                                    </div>
                                                </div>
                                            ) : (
                                                <span className="text-gray-300 italic text-xs">Processing...</span>
                                            )}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default Reports;
