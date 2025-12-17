import React, { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import './Input.css';

const Input = ({
    label,
    type = 'text',
    name,
    value,
    onChange,
    placeholder,
    error,
    icon: Icon,
    className = '',
    required = false,
    ...props
}) => {
    const [showPassword, setShowPassword] = useState(false);
    const isPassword = type === 'password';
    const inputType = isPassword ? (showPassword ? 'text' : 'password') : type;

    return (
        <div className={`form-group ${className}`}>
            {label && (
                <label htmlFor={name} className="form-label">
                    {label} {required && <span className="required">*</span>}
                </label>
            )}

            <div className={`input-wrapper ${error ? 'has-error' : ''}`}>
                {Icon && <Icon size={18} className="input-icon" />}

                <input
                    type={inputType}
                    id={name}
                    name={name}
                    value={value}
                    onChange={onChange}
                    placeholder={placeholder}
                    className={`form-input ${Icon ? 'has-icon' : ''}`}
                    required={required}
                    {...props}
                />

                {isPassword && (
                    <button
                        type="button"
                        className="password-toggle"
                        onClick={() => setShowPassword(!showPassword)}
                        tabIndex="-1"
                    >
                        {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                )}
            </div>

            {error && <p className="input-error-message">{error}</p>}
        </div>
    );
};

export default Input;
