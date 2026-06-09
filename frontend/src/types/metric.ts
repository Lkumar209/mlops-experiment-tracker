export interface MetricPoint {
  step: number;
  value: number;
  logged_at: string;
}

export interface MetricSeries {
  runId: string;
  key: string;
  points: MetricPoint[];
}
