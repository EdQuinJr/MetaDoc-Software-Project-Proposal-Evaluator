import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
  FileText,
  LayoutDashboard,
  Upload,
  Calendar,
  FileBarChart,
  LogOut,
  Menu,
  X,
  User,
  BookCheck,
} from 'lucide-react';
import logo from '../../assets/images/logo.png';
import '../../styles/DashboardLayout.css';

const DashboardLayout = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Overview' },
    { path: '/dashboard/folders', icon: FileText, label: 'Folders' },
    { path: '/dashboard/deadlines', icon: Calendar, label: 'Deadlines' },
    { path: '/dashboard/rubrics', icon: BookCheck, label: 'Rubrics' },
    { path: '/dashboard/reports', icon: FileBarChart, label: 'Reports' },
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
        </nav>

        <div className="sidebar-footer">
          <button className="btn-logout" onClick={handleLogout}>
            <LogOut size={18} />
            <span>Logout</span>
          </button>
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
    </div>
  );
};

export default DashboardLayout;
