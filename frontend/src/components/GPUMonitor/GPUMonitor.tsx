import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import type { AppDispatch, RootState } from '../../store';
import { fetchGPUNodes } from '../../store/gpuSlice';
import { NodeCard } from './NodeCard';

export const GPUMonitor: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { nodes, loading, error } = useSelector((s: RootState) => s.gpu);

  useEffect(() => {
    dispatch(fetchGPUNodes());
    const interval = setInterval(() => dispatch(fetchGPUNodes()), 10000);
    return () => clearInterval(interval);
  }, [dispatch]);

  return (
    <div style={{ padding: 24 }}>
      <h1 style={{ color: '#e2e8f0', fontSize: 22, fontWeight: 700, marginBottom: 24 }}>GPU Monitor</h1>
      {error && <div style={{ color: '#ef4444', marginBottom: 12 }}>{error}</div>}
      {loading && nodes.length === 0 ? (
        <div style={{ color: '#64748b', textAlign: 'center', padding: 48 }}>Loading GPU nodes...</div>
      ) : nodes.length === 0 ? (
        <div style={{ color: '#64748b', textAlign: 'center', padding: 48 }}>No GPU nodes registered</div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 16 }}>
          {nodes.map((node) => (
            <NodeCard key={node.id} node={node} />
          ))}
        </div>
      )}
    </div>
  );
};
