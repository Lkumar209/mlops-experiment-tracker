export type RunStatus = 'queued' | 'running' | 'completed' | 'failed';

export interface Run {
  id: string;
  experiment_id: string;
  name: string;
  status: RunStatus;
  hyperparameters: Record<string, unknown>;
  gpu_node_id: string | null;
  started_at: string | null;
  finished_at: string | null;
  created_at: string;
}
