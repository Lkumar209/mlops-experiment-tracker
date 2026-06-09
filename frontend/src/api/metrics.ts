import { apiClient } from './client';
import type { MetricPoint } from '../types/metric';

export const metricsApi = {
  getKeys: (runId: string) =>
    apiClient.get<{ data: string[] }>(`/runs/${runId}/metrics`).then((r) => r.data.data),

  getLossCurve: (runId: string, key: string) =>
    apiClient
      .get<{ data: MetricPoint[] }>(`/runs/${runId}/metrics/${key}`)
      .then((r) => r.data.data),

  compare: (runId: string, key: string, runIds: string[]) =>
    apiClient
      .get<{ data: Record<string, MetricPoint[]> }>(`/runs/${runId}/metrics/compare`, {
        params: { key, run_ids: runIds.join(',') },
      })
      .then((r) => r.data.data),
};
