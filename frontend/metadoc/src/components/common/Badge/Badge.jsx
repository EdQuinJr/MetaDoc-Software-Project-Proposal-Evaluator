import React from 'react';
import './Badge.css';

const Badge = ({ children, variant = 'info', icon: Icon, className = '' }) => {
    return (
        <span className={`badge badge-${variant} ${className}`}>
            {Icon && <Icon size={14} className="badge-icon" />}
            {children}
        </span>
    );
};

export default Badge;
