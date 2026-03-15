import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
  Folder,
  LayoutDashboard,
  FileBarChart,
  LogOut,
  Menu,
  X,
  User,
  Users,
  XCircle,
  Code2,
  Globe,
  Database,
  ClipboardList,
} from 'lucide-react';
import logo from '../../assets/images/logo.png';
import citLogo from '../../assets/images/cit_logo.png';
import quindaoProfile from '../../assets/images/members/Quindao_Profile.jpg';
import abellanaProfile from '../../assets/images/members/Abellana_Profile.jpg';
import velosoProfile from '../../assets/images/members/Veloso_Profile.jpg';
import garingProfile from '../../assets/images/members/Garing_Profile.jpg';
import '../../styles/DashboardLayout.css';

const DashboardLayout = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showTeamModal, setShowTeamModal] = useState(false);
  const [selectedMember, setSelectedMember] = useState(null);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Overview' },
    { path: '/dashboard/deliverables', icon: Folder, label: 'Deliverable' },
    { path: '/dashboard/class-record', icon: Users, label: 'Class Record' },
    { path: '/dashboard/reports', icon: FileBarChart, label: 'Reports' },
  ];

  const teamMembers = [
    {
      name: 'Quindao',
      role: 'Project Manager',
      Icon: ClipboardList,
      photo: quindaoProfile,
      description: 'Leads planning, sprint coordination, and delivery timelines for MetaDoc. Ensures features are aligned with project goals and keeps the team on track through milestone-based execution.',
    },
    {
      name: 'Abellana',
      role: 'Project Manager',
      Icon: ClipboardList,
      photo: abellanaProfile,
      description: 'Manages documentation flow, task prioritization, and team communication. Supports risk mitigation and helps maintain quality and progress visibility across all development phases.',
    },
    {
      name: 'Veloso',
      role: 'Frontend Developer',
      Icon: Globe,
      photo: velosoProfile,
      description: 'Builds and refines the MetaDoc user interface, focusing on usability, consistency, and responsive behavior. Translates functional requirements into clean and intuitive UI components.',
    },
    {
      name: 'Garing',
      role: 'Full Stack Developer',
      Icon: Code2,
      photo: garingProfile,
      description: 'Implements end-to-end features across frontend and backend. Handles API integration, data flow, and system behavior to ensure seamless functionality throughout the MetaDoc platform.',
    },
  ];

  const isActive = (path) => {
    if (path === '/dashboard') {
      return location.pathname === '/dashboard';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <div className="dashboard-layout">
      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <img src={logo} alt="MetaDoc Logo" className="sidebar-logo-img" />
            <span className="logo-text">MetaDoc</span>
          </div>
          <button
            className="sidebar-close"
            onClick={() => setSidebarOpen(false)}
          >
            <X size={24} />
          </button>
        </div>

        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-item ${isActive(item.path) ? 'nav-item-active' : ''}`}
              onClick={() => setSidebarOpen(false)}
            >
              <item.icon size={20} />
              <span>{item.label}</span>
            </Link>
          ))}

          <button
            type="button"
            className="nav-item nav-item-button"
            onClick={() => {
              setShowTeamModal(true);
              setSidebarOpen(false);
            }}
          >
            <Code2 size={20} />
            <span>Team 7</span>
          </button>
        </nav>

        <div className="sidebar-footer">
          <button className="btn-logout" onClick={handleLogout}>
            <LogOut size={18} />
            <span>Logout</span>
          </button>
          <div className="sidebar-version">MetaDoc V1.0</div>
          <div className="sidebar-cit">
            <img src={citLogo} alt="CIT University" width={20} height={20} style={{ objectFit: 'contain', opacity: 0.75 }} />
            <span>CIT University</span>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="main-content">
        {/* Top Bar */}
        <header className="topbar">
          <button
            className="menu-toggle"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            <Menu size={24} />
          </button>

          <div className="topbar-right">
            <div className="user-badge">
              <div className="user-avatar-small">
                {user?.profile_picture ? (
                  <img src={user.profile_picture} alt={user.name} />
                ) : (
                  <User size={16} />
                )}
              </div>
              <span className="user-name-small">{user?.name}</span>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="page-content">{children}</main>
      </div>

      {/* Sidebar Overlay */}
      {sidebarOpen && (
        <div
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
        ></div>
      )}

      {showTeamModal && (
        <div className="team-modal-overlay" onClick={() => { setShowTeamModal(false); setSelectedMember(null); }}>
          <div className={`team-modal${selectedMember ? ' team-modal-wide' : ''}`} onClick={(e) => e.stopPropagation()}>
            {/* Left panel */}
            <div className="team-panel-left">
              <div className="team-modal-header">
                <div className="team-modal-title-wrap">
                  <h2>Team 7</h2>
                  <p>Core developers behind MetaDoc</p>
                </div>
                <button
                  type="button"
                  className="team-modal-close"
                  onClick={() => { setShowTeamModal(false); setSelectedMember(null); }}
                  aria-label="Close Team 7 modal"
                >
                  <XCircle size={20} />
                </button>
              </div>
              <div className="team-grid">
                {teamMembers.map((member) => (
                  <article
                    key={member.name}
                    className={`team-card team-card-clickable${selectedMember?.name === member.name ? ' team-card-active' : ''}`}
                    onClick={() => setSelectedMember(member)}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => e.key === 'Enter' && setSelectedMember(member)}
                  >
                    {member.photo ? (
                      <img src={member.photo} alt={member.name} className="team-card-avatar" />
                    ) : (
                      <div className="team-card-icon">
                        <member.Icon size={18} />
                      </div>
                    )}
                    <div className="team-card-content">
                      <h3>{member.name}</h3>
                      <p>{member.role}</p>
                    </div>
                  </article>
                ))}
              </div>
            </div>

            {/* Right panel — slides in when a member is selected */}
            {selectedMember && (
              <div className="team-panel-right">
                <div className="team-panel-right-header">
                  <h3>{selectedMember.name}</h3>
                  <button
                    type="button"
                    className="team-modal-close"
                    onClick={() => setSelectedMember(null)}
                    aria-label="Close member details"
                  >
                    <XCircle size={18} />
                  </button>
                </div>
                {selectedMember.photo ? (
                  <img src={selectedMember.photo} alt={selectedMember.name} className="team-member-photo-large" />
                ) : (
                  <div className="team-member-icon-large">
                    <selectedMember.Icon size={36} />
                  </div>
                )}
                <p className="team-member-role-label">{selectedMember.role}</p>
                <p className="team-member-description">{selectedMember.description}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardLayout;
