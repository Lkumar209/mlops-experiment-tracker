import { useEffect, useRef } from 'react';
import { useDispatch } from 'react-redux';
import { sseBaseUrl, sseApiKey } from '../api/client';
import { appendMetricPoint } from '../store/metricsSlice';
import type { MetricPoint } from '../types/metric';

export function useMetricsStream(runId: string, enabled: boolean): void {
  const dispatch = useDispatch();
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!enabled || !runId) return;

    const url = `${sseBaseUrl}/runs/${runId}/metrics/stream?api_key=${sseApiKey}`;
    const es = new EventSource(url);
    esRef.current = es;

    es.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as {
          run_id: string;
          key: string;
          value: number;
          step: number;
          logged_at: string;
        };
        if (data.key && data.value !== undefined) {
          const point: MetricPoint = { step: data.step, value: data.value, logged_at: data.logged_at };
          dispatch(appendMetricPoint({ runId, key: data.key, point }));
        }
      } catch {
        // skip malformed messages
      }
    };

    es.onerror = () => {
      es.close();
    };

    return () => {
      es.close();
      esRef.current = null;
    };
  }, [runId, enabled, dispatch]);
}
