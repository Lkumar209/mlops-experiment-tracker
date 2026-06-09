import React from 'react';
import { StatusBadge } from '../shared/StatusBadge';
import type { GPUNode } from '../../store/gpuSlice';

interface NodeCardProps {
  node: GPUNode;
}

export const NodeCard: React.FC<NodeCardProps> = ({ node }) => (
  <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, padding: 16 }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
      <h3 style={{ color: '#e2e8f0', fontSize: 14, fontWeight: 600 }}>{node.name}</h3>
      <StatusBadge status={node.status} />
    </div>
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, fontSize: 12 }}>
      <div>
        <span style={{ color: '#64748b' }}>GPUs</span>
        <div style={{ color: '#e2e8f0', fontWeight: 600, fontSize: 18 }}>{node.gpu_count}</div>
      </div>
      <div>
        <span style={{ color: '#64748b' }}>Memory</span>
        <div style={{ color: '#e2e8f0', fontWeight: 600, fontSize: 18 }}>{node.memory_gb} GB</div>
      </div>
    </div>
    {node.current_run_id && (
      <div style={{ marginTop: 10, padding: '6px 10px', background: '#0f172a', borderRadius: 6, fontSize: 11, color: '#94a3b8' }}>
        Run: {node.current_run_id.slice(0, 16)}...
      </div>
    )}
    {node.last_heartbeat && (
      <div style={{ marginTop: 6, fontSize: 11, color: '#475569' }}>
        Heartbeat: {new Date(node.last_heartbeat).toLocaleTimeString()}
      </div>
    )}
  </div>
);
