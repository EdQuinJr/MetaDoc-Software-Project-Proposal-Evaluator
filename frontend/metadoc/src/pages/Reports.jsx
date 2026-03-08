import React, { useState } from 'react';
import {
    FileBarChart,
    MessageSquare,
    PieChart,
    TrendingUp
} from 'lucide-react';
import Card from '../components/common/Card/Card';
import Button from '../components/common/Button/Button';
import '../styles/Reports.css';

const Reports = () => {
    const [activeTab, setActiveTab] = useState('summary');

    const tabs = [
        { id: 'summary', label: 'Analysis Summary', icon: FileBarChart },
        { id: 'feedback', label: 'Feedback', icon: MessageSquare },
        { id: 'analytics', label: 'Analytics Charts', icon: PieChart },
    ];

    const renderTabContent = () => {
        switch (activeTab) {
            case 'summary':
                return (
                    <div className="tab-pane fade-in">
                        <div className="tab-header">
                            <h3>Analysis Summary</h3>
                            <p>Overview of document submissions and evaluation status.</p>
                        </div>
                        <div className="empty-state">
                            <FileBarChart size={48} />
                            <p>Summary report data will be displayed here.</p>
                        </div>
                    </div>
                );
            case 'feedback':
                return (
                    <div className="tab-pane fade-in">
                        <div className="tab-header">
                            <h3>Student Feedback</h3>
                            <p>Summary of insights and automated feedback provided to students.</p>
                        </div>
                        <div className="empty-state">
                            <MessageSquare size={48} />
                            <p>Aggregated feedback data will be displayed here.</p>
                        </div>
                    </div>
                );
            case 'analytics':
                return (
                    <div className="tab-pane fade-in">
                        <div className="tab-header">
                            <h3>Analytics Charts</h3>
                            <p>Visual representation of proposal metrics and performance trends.</p>
                        </div>
                        <div className="empty-state">
                            <PieChart size={48} />
                            <p>Advanced data visualizations will be displayed here.</p>
                        </div>
                    </div>
                );
            default:
                return null;
        }
    };

    return (
        <div className="reports-page">
            <div className="reports-container">
                <header className="reports-header">
                    <div className="header-title">
                        <TrendingUp size={24} className="text-maroon" />
                        <h1>Analysis Reports</h1>
                    </div>
                    <div className="header-actions">
                    </div>
                </header>

                <div className="reports-layout">
                    {/* Internal Navigation Tabs */}
                    <nav className="reports-nav">
                        {tabs.map((tab) => (
                            <button
                                key={tab.id}
                                className={`reports-nav-item ${activeTab === tab.id ? 'active' : ''}`}
                                onClick={() => setActiveTab(tab.id)}
                            >
                                <tab.icon size={18} />
                                <span>{tab.label}</span>
                            </button>
                        ))}
                    </nav>

                    {/* Main Content Area */}
                    <main className="reports-main">
                        <Card className="reports-content-card">
                            {renderTabContent()}
                        </Card>
                    </main>
                </div>
            </div>
        </div>
    );
};

export default Reports;
