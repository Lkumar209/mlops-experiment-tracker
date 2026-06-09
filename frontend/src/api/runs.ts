import { apiClient } from './client';
import type { Run, RunStatus } from '../types/run';

export const runsApi = {
  list: (experimentId: string, params?: { page?: number; per_page?: number; status?: RunStatus }) =>
    apiClient
      .get<{ data: Run[]; meta: { page: number; total: number } }>(`/experiments/${experimentId}/runs`, { params })
      .then((r) => r.data),

  get: (runId: string) =>
    apiClient.get<{ data: Run }>(`/runs/${runId}`).then((r) => r.data.data),

  create: (experimentId: string, payload: { name: string; hyperparameters?: Record<string, unknown> }) =>
    apiClient
      .post<{ data: Run }>(`/experiments/${experimentId}/runs`, payload)
      .then((r) => r.data.data),

  updateStatus: (runId: string, status: RunStatus) =>
    apiClient.patch<{ data: Run }>(`/runs/${runId}/status`, { status }).then((r) => r.data.data),

  delete: (runId: string) =>
    apiClient.delete<{ data: { deleted: boolean } }>(`/runs/${runId}`).then((r) => r.data.data),
};
