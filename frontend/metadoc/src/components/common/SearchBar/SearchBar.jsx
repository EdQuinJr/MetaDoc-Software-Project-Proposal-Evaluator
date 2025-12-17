import React from 'react';
import { Search } from 'lucide-react';
import './SearchBar.css';

const SearchBar = ({ value, onChange, placeholder = 'Search...', className = '' }) => {
    return (
        <div className={`search-bar ${className}`}>
            <Search size={20} className="search-icon" />
            <input
                type="text"
                value={value}
                onChange={(e) => onChange(e.target.value)}
                placeholder={placeholder}
                className="search-input"
            />
        </div>
    );
};

export default SearchBar;
