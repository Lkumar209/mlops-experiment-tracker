import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import type { AppDispatch, RootState } from '../../store';
import { fetchExperiments } from '../../store/experimentsSlice';
import { fetchGPUNodes } from '../../store/gpuSlice';
import { ExperimentList } from '../ExperimentList/ExperimentList';

export const Dashboard: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { items: experiments, meta } = useSelector((s: RootState) => s.experiments);
  const gpuNodes = useSelector((s: RootState) => s.gpu.nodes);

  const activeGPUs = gpuNodes.filter((n) => n.status === 'busy').length;
  const completedToday = experiments.reduce((acc) => acc, 0);

  useEffect(() => {
    dispatch(fetchExperiments());
    dispatch(fetchGPUNodes());

    const interval = setInterval(() => {
      dispatch(fetchExperiments());
      dispatch(fetchGPUNodes());
    }, 30000);

    return () => clearInterval(interval);
  }, [dispatch]);

  const metricCards = [
    { label: 'Total Experiments', value: meta.total, color: '#7c3aed' },
    { label: 'Total Runs', value: experiments.reduce((acc, e) => acc + ((e as any).total_runs || 0), 0), color: '#3b82f6' },
    { label: 'Active GPU Nodes', value: activeGPUs, color: '#f59e0b' },
    { label: 'Completed Runs Today', value: completedToday, color: '#22c55e' },
  ];

  return (
    <div style={{ padding: 24 }}>
      <h1 style={{ color: '#e2e8f0', fontSize: 22, fontWeight: 700, marginBottom: 24 }}>Dashboard</h1>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 32 }}>
        {metricCards.map((card) => (
          <div key={card.label} style={{ background: '#1e293b', borderRadius: 8, padding: 20, borderLeft: `4px solid ${card.color}` }}>
            <div style={{ color: '#64748b', fontSize: 12, marginBottom: 4 }}>{card.label}</div>
            <div style={{ color: '#e2e8f0', fontSize: 28, fontWeight: 700 }}>{card.value}</div>
          </div>
        ))}
      </div>

      <div style={{ marginBottom: 32 }}>
        <h2 style={{ color: '#94a3b8', fontSize: 14, marginBottom: 16, textTransform: 'uppercase', letterSpacing: 1 }}>Experiments</h2>
        <ExperimentList />
      </div>
    </div>
  );
};
