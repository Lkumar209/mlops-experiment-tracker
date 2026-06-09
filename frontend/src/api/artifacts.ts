import { apiClient } from './client';
import type { Artifact } from '../types/artifact';

export const artifactsApi = {
  list: (runId: string) =>
    apiClient
      .get<{ data: Artifact[]; meta: { total: number } }>(`/runs/${runId}/artifacts`)
      .then((r) => r.data),

  get: (artifactId: string) =>
    apiClient.get<{ data: Artifact }>(`/artifacts/${artifactId}`).then((r) => r.data.data),

  getLineage: (artifactId: string) =>
    apiClient.get<{ data: unknown[] }>(`/artifacts/${artifactId}/lineage`).then((r) => r.data.data),

  create: (
    runId: string,
    payload: {
      name: string;
      artifact_type: string;
      uri: string;
      size_bytes?: number;
      checksum?: string;
      parent_artifact_id?: string;
    }
  ) =>
    apiClient.post<{ data: Artifact }>(`/runs/${runId}/artifacts`, payload).then((r) => r.data.data),
};
