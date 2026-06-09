import React, { useState } from 'react';
import { useExperiments } from '../../hooks/useExperiments';
import { ExperimentCard } from './ExperimentCard';

export const ExperimentList: React.FC = () => {
  const [search, setSearch] = useState('');
  const { experiments, loading, error } = useExperiments();

  const filtered = experiments.filter((e) =>
    e.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <input
          type="text"
          placeholder="Search experiments..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{
            width: '100%',
            padding: '8px 12px',
            background: '#0f172a',
            border: '1px solid #334155',
            borderRadius: 6,
            color: '#e2e8f0',
            fontSize: 14,
          }}
        />
      </div>
      {error && <div style={{ color: '#ef4444', marginBottom: 12 }}>{error}</div>}
      {loading ? (
        <div style={{ color: '#64748b', textAlign: 'center', padding: 32 }}>Loading experiments...</div>
      ) : filtered.length === 0 ? (
        <div style={{ color: '#64748b', textAlign: 'center', padding: 32 }}>No experiments found</div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 16 }}>
          {filtered.map((exp) => (
            <ExperimentCard key={exp.id} experiment={exp} />
          ))}
        </div>
      )}
    </div>
  );
};
