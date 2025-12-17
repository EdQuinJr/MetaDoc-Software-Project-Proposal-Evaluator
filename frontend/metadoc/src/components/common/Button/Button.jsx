import React from 'react';
import './Button.css';

const Button = ({
    children,
    variant = 'primary',
    size = 'medium',
    className = '',
    loading = false,
    disabled,
    icon: Icon,
    type = 'button',
    onClick,
    ...props
}) => {
    return (
        <button
            type={type}
            className={`btn btn-${variant} btn-${size} ${className}`}
            disabled={disabled || loading}
            onClick={onClick}
            {...props}
        >
            {loading ? (
                <div className="btn-spinner"></div>
            ) : Icon ? (
                <Icon size={size === 'small' ? 16 : 20} className="btn-icon" />
            ) : null}

            {children && <span className="btn-text">{children}</span>}
        </button>
    );
};

export default Button;
