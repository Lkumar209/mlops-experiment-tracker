import React from 'react';
import { useNavigate } from 'react-router-dom';
import type { Experiment } from '../../types/experiment';

interface ExperimentCardProps {
  experiment: Experiment & { total_runs?: number; completed_runs?: number; failed_runs?: number };
}

export const ExperimentCard: React.FC<ExperimentCardProps> = ({ experiment }) => {
  const navigate = useNavigate();

  return (
    <div
      onClick={() => navigate(`/experiments/${experiment.id}`)}
      style={{
        background: '#1e293b',
        border: '1px solid #334155',
        borderRadius: 8,
        padding: 16,
        cursor: 'pointer',
        transition: 'border-color 0.2s',
      }}
      onMouseEnter={(e) => (e.currentTarget.style.borderColor = '#7c3aed')}
      onMouseLeave={(e) => (e.currentTarget.style.borderColor = '#334155')}
    >
      <h3 style={{ color: '#e2e8f0', fontSize: 15, marginBottom: 6 }}>{experiment.name}</h3>
      {experiment.description && (
        <p style={{ color: '#64748b', fontSize: 12, marginBottom: 8, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {experiment.description}
        </p>
      )}
      <div style={{ display: 'flex', gap: 12, fontSize: 12, color: '#94a3b8' }}>
        <span>Runs: {experiment.total_runs ?? 0}</span>
        <span style={{ color: '#22c55e' }}>✓ {experiment.completed_runs ?? 0}</span>
        <span style={{ color: '#ef4444' }}>✗ {experiment.failed_runs ?? 0}</span>
      </div>
      {Object.keys(experiment.tags || {}).length > 0 && (
        <div style={{ marginTop: 8, display: 'flex', flexWrap: 'wrap', gap: 4 }}>
          {Object.entries(experiment.tags).map(([k, v]) => (
            <span key={k} style={{ background: '#7c3aed22', color: '#a78bfa', padding: '2px 8px', borderRadius: 8, fontSize: 11 }}>
              {k}: {v}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};
