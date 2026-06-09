import React from 'react';
import type { RunStatus } from '../../types/run';

const COLOR_MAP: Record<string, string> = {
  queued: '#94a3b8',
  running: '#3b82f6',
  completed: '#22c55e',
  failed: '#ef4444',
  available: '#22c55e',
  busy: '#f59e0b',
  offline: '#ef4444',
};

interface StatusBadgeProps {
  status: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const color = COLOR_MAP[status] || '#94a3b8';
  return (
    <span
      style={{
        display: 'inline-block',
        padding: '2px 10px',
        borderRadius: 12,
        background: `${color}22`,
        color,
        border: `1px solid ${color}`,
        fontSize: 12,
        fontWeight: 600,
        textTransform: 'capitalize',
      }}
    >
      {status}
    </span>
  );
};
