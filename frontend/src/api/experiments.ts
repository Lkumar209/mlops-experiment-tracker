import { apiClient } from './client';
import type { Experiment } from '../types/experiment';

export interface PaginatedResponse<T> {
  data: T[];
  meta: { page: number; per_page: number; total: number };
}

export const experimentsApi = {
  list: (params?: { page?: number; per_page?: number; tags?: string; sort_by?: string }) =>
    apiClient.get<PaginatedResponse<Experiment>>('/experiments', { params }).then((r) => r.data),

  get: (id: string) =>
    apiClient.get<{ data: Experiment }>(`/experiments/${id}`).then((r) => r.data.data),

  create: (payload: { name: string; description?: string; tags?: Record<string, string> }) =>
    apiClient.post<{ data: Experiment }>('/experiments', payload).then((r) => r.data.data),

  update: (id: string, payload: { name?: string; description?: string; tags?: Record<string, string> }) =>
    apiClient.put<{ data: Experiment }>(`/experiments/${id}`, payload).then((r) => r.data.data),

  delete: (id: string) =>
    apiClient.delete<{ data: { deleted: boolean } }>(`/experiments/${id}`).then((r) => r.data.data),
};
