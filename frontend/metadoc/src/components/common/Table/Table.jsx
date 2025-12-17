import React from 'react';
import './Table.css';

const Table = ({ columns, data, onRowClick, emptyMessage, renderCell }) => {
    if (!data || data.length === 0) {
        return (
            <div className="table-empty-state">
                <p>{emptyMessage || 'No data available'}</p>
            </div>
        );
    }

    return (
        <div className="table-container">
            <table className="data-table">
                <thead>
                    <tr>
                        {columns.map((col, index) => (
                            <th key={index} className={col.className || ''}>
                                {col.header}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {data.map((item, rowIndex) => (
                        <tr
                            key={item.id || rowIndex}
                            className={onRowClick ? 'clickable-row' : ''}
                            onClick={() => onRowClick && onRowClick(item)}
                        >
                            {columns.map((col, colIndex) => (
                                <td key={colIndex} className={col.className || ''}>
                                    {renderCell ? renderCell(item, col) : (col.field ? item[col.field] : null)}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default Table;
