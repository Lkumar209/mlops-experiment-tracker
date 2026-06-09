import React from 'react';

interface HyperparamTableProps {
  hyperparameters: Record<string, unknown>;
  compareRun?: Record<string, unknown>;
}

export const HyperparamTable: React.FC<HyperparamTableProps> = ({ hyperparameters, compareRun }) => {
  const keys = Array.from(new Set([...Object.keys(hyperparameters), ...Object.keys(compareRun || {})]));

  return (
    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
      <thead>
        <tr>
          <th style={{ textAlign: 'left', padding: '6px 12px', color: '#64748b', borderBottom: '1px solid #334155' }}>Parameter</th>
          <th style={{ textAlign: 'left', padding: '6px 12px', color: '#64748b', borderBottom: '1px solid #334155' }}>Value</th>
          {compareRun && (
            <th style={{ textAlign: 'left', padding: '6px 12px', color: '#64748b', borderBottom: '1px solid #334155' }}>Compare</th>
          )}
        </tr>
      </thead>
      <tbody>
        {keys.map((key) => {
          const val = hyperparameters[key];
          const cmpVal = compareRun?.[key];
          const differs = compareRun && JSON.stringify(val) !== JSON.stringify(cmpVal);

          return (
            <tr key={key} style={{ background: differs ? '#f59e0b11' : 'transparent' }}>
              <td style={{ padding: '6px 12px', color: '#94a3b8', borderBottom: '1px solid #1e293b' }}>{key}</td>
              <td style={{ padding: '6px 12px', color: differs ? '#f59e0b' : '#e2e8f0', borderBottom: '1px solid #1e293b', fontFamily: 'monospace' }}>
                {String(val ?? '—')}
              </td>
              {compareRun && (
                <td style={{ padding: '6px 12px', color: differs ? '#f59e0b' : '#64748b', borderBottom: '1px solid #1e293b', fontFamily: 'monospace' }}>
                  {String(cmpVal ?? '—')}
                </td>
              )}
            </tr>
          );
        })}
      </tbody>
    </table>
  );
};
