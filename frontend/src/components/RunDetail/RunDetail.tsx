import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import type { AppDispatch, RootState } from '../../store';
import { fetchRun } from '../../store/runsSlice';
import { fetchMetricKeys } from '../../store/metricsSlice';
import { LossCurve } from './LossCurve';
import { HyperparamTable } from './HyperparamTable';
import { StatusBadge } from '../shared/StatusBadge';

export const RunDetail: React.FC = () => {
  const { runId } = useParams<{ runId: string }>();
  const dispatch = useDispatch<AppDispatch>();
  const run = useSelector((s: RootState) => s.runs.selected);
  const metricKeys = useSelector((s: RootState) => (runId ? s.metrics.keys[runId] || [] : []));
  const [selectedKey, setSelectedKey] = useState<string>('');

  useEffect(() => {
    if (runId) {
      dispatch(fetchRun(runId));
      dispatch(fetchMetricKeys(runId));
    }
  }, [dispatch, runId]);

  useEffect(() => {
    if (metricKeys.length > 0 && !selectedKey) {
      setSelectedKey(metricKeys[0]);
    }
  }, [metricKeys, selectedKey]);

  if (!run) return <div style={{ padding: 32, color: '#64748b' }}>Loading run...</div>;

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24 }}>
        <h1 style={{ color: '#e2e8f0', fontSize: 22, fontWeight: 700 }}>{run.name}</h1>
        <StatusBadge status={run.status} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 24 }}>
        <div style={{ background: '#1e293b', borderRadius: 8, padding: 16 }}>
          <h2 style={{ color: '#94a3b8', fontSize: 13, marginBottom: 12, textTransform: 'uppercase', letterSpacing: 1 }}>Hyperparameters</h2>
          <HyperparamTable hyperparameters={run.hyperparameters} />
        </div>
        <div style={{ background: '#1e293b', borderRadius: 8, padding: 16 }}>
          <h2 style={{ color: '#94a3b8', fontSize: 13, marginBottom: 12, textTransform: 'uppercase', letterSpacing: 1 }}>Run Info</h2>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, fontSize: 13 }}>
            <span style={{ color: '#64748b' }}>Started</span>
            <span style={{ color: '#e2e8f0' }}>{run.started_at ? new Date(run.started_at).toLocaleString() : '—'}</span>
            <span style={{ color: '#64748b' }}>Finished</span>
            <span style={{ color: '#e2e8f0' }}>{run.finished_at ? new Date(run.finished_at).toLocaleString() : '—'}</span>
            <span style={{ color: '#64748b' }}>GPU Node</span>
            <span style={{ color: '#e2e8f0' }}>{run.gpu_node_id ?? 'None'}</span>
          </div>
        </div>
      </div>

      {metricKeys.length > 0 && (
        <div>
          <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
            {metricKeys.map((key) => (
              <button
                key={key}
                onClick={() => setSelectedKey(key)}
                style={{
                  padding: '4px 12px',
                  borderRadius: 6,
                  border: '1px solid',
                  borderColor: selectedKey === key ? '#7c3aed' : '#334155',
                  background: selectedKey === key ? '#7c3aed22' : 'transparent',
                  color: selectedKey === key ? '#a78bfa' : '#64748b',
                  cursor: 'pointer',
                  fontSize: 12,
                }}
              >
                {key}
              </button>
            ))}
          </div>
          {selectedKey && <LossCurve runId={run.id} metricKey={selectedKey} runStatus={run.status} />}
        </div>
      )}
    </div>
  );
};
