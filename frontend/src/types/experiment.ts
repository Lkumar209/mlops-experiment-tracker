export interface Experiment {
  id: string;
  name: string;
  description: string | null;
  tags: Record<string, string>;
  created_at: string;
  updated_at: string;
  runs?: Run[];
}

export interface ExperimentSummary extends Experiment {
  total_runs: number;
  completed_runs: number;
  failed_runs: number;
  first_run_at: string | null;
  last_run_at: string | null;
}

import type { Run } from './run';
