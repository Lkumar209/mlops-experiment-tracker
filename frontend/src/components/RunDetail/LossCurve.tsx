import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { AppDispatch, RootState } from '../../store';
import { fetchLossCurve, fetchCompareMetrics } from '../../store/metricsSlice';
import { useMetricsStream } from '../../hooks/useMetricsStream';

const COLORS = ['#818cf8', '#34d399', '#f59e0b', '#f87171', '#a78bfa', '#60a5fa'];

interface LossCurveProps {
  runId: string;
  metricKey: string;
  runStatus?: string;
  compareRunIds?: string[];
  compareRunNames?: Record<string, string>;
}

export const LossCurve: React.FC<LossCurveProps> = ({
  runId,
  metricKey,
  runStatus,
  compareRunIds = [],
  compareRunNames = {},
}) => {
  const dispatch = useDispatch<AppDispatch>();
  const isRunning = runStatus === 'running';

  const curve = useSelector((s: RootState) => s.metrics.curves[runId]?.[metricKey] || []);
  const compareData = useSelector((s: RootState) => s.metrics.compareData[metricKey] || {});
  const loading = useSelector((s: RootState) => s.metrics.loading);

  useMetricsStream(runId, isRunning);

  useEffect(() => {
    if (compareRunIds.length > 0) {
      dispatch(fetchCompareMetrics({ runId, key: metricKey, runIds: compareRunIds }));
    } else {
      dispatch(fetchLossCurve({ runId, key: metricKey }));
    }
  }, [dispatch, runId, metricKey, compareRunIds.join(',')]);

  const allRunIds = compareRunIds.length > 0 ? [runId, ...compareRunIds] : [runId];
  const allData = compareRunIds.length > 0 ? compareData : { [runId]: curve };

  const maxStep = Math.max(...allRunIds.flatMap((id) => (allData[id] || []).map((p) => p.step)), 0);
  const mergedData: Record<number, Record<string, number>> = {};
  allRunIds.forEach((id) => {
    (allData[id] || []).forEach((point) => {
      if (!mergedData[point.step]) mergedData[point.step] = { step: point.step };
      mergedData[point.step][id] = point.value;
    });
  });
  const chartData = Object.values(mergedData).sort((a, b) => a.step - b.step);

  if (loading && chartData.length === 0) {
    return (
      <div style={{ height: 240, display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#1e293b', borderRadius: 8, color: '#64748b' }}>
        Loading {metricKey}...
      </div>
    );
  }

  return (
    <div style={{ background: '#1e293b', borderRadius: 8, padding: 16 }}>
      <div style={{ fontSize: 13, color: '#94a3b8', marginBottom: 8, display: 'flex', justifyContent: 'space-between' }}>
        <span>{metricKey}</span>
        {isRunning && <span style={{ color: '#3b82f6', fontSize: 11 }}>● LIVE</span>}
      </div>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="step" tick={{ fill: '#64748b', fontSize: 11 }} />
          <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
          <Tooltip
            contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 6 }}
            labelStyle={{ color: '#94a3b8' }}
            itemStyle={{ color: '#e2e8f0' }}
          />
          {allRunIds.length > 1 && <Legend wrapperStyle={{ fontSize: 12, color: '#94a3b8' }} />}
          {allRunIds.map((id, idx) => (
            <Line
              key={id}
              type="monotone"
              dataKey={id}
              name={compareRunNames[id] || (id === runId ? 'This run' : id.slice(0, 8))}
              stroke={COLORS[idx % COLORS.length]}
              dot={false}
              strokeWidth={2}
              isAnimationActive={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
