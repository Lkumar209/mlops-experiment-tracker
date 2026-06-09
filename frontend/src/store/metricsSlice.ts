import { createAsyncThunk, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { metricsApi } from '../api/metrics';
import type { MetricPoint } from '../types/metric';

interface MetricsState {
  keys: Record<string, string[]>;
  curves: Record<string, Record<string, MetricPoint[]>>;
  compareData: Record<string, Record<string, MetricPoint[]>>;
  loading: boolean;
  error: string | null;
}

const initialState: MetricsState = {
  keys: {},
  curves: {},
  compareData: {},
  loading: false,
  error: null,
};

export const fetchMetricKeys = createAsyncThunk('metrics/fetchKeys', async (runId: string) => {
  const keys = await metricsApi.getKeys(runId);
  return { runId, keys };
});

export const fetchLossCurve = createAsyncThunk(
  'metrics/fetchLossCurve',
  async ({ runId, key }: { runId: string; key: string }) => {
    const points = await metricsApi.getLossCurve(runId, key);
    return { runId, key, points };
  }
);

export const fetchCompareMetrics = createAsyncThunk(
  'metrics/fetchCompare',
  async ({ runId, key, runIds }: { runId: string; key: string; runIds: string[] }) => {
    const data = await metricsApi.compare(runId, key, runIds);
    return { key, data };
  }
);

const metricsSlice = createSlice({
  name: 'metrics',
  initialState,
  reducers: {
    appendMetricPoint: (
      state,
      action: PayloadAction<{ runId: string; key: string; point: MetricPoint }>
    ) => {
      const { runId, key, point } = action.payload;
      if (!state.curves[runId]) state.curves[runId] = {};
      if (!state.curves[runId][key]) state.curves[runId][key] = [];
      state.curves[runId][key].push(point);
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchMetricKeys.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchMetricKeys.fulfilled, (state, action) => {
        state.loading = false;
        state.keys[action.payload.runId] = action.payload.keys;
      })
      .addCase(fetchMetricKeys.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message ?? 'Failed to fetch metric keys';
      })
      .addCase(fetchLossCurve.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchLossCurve.fulfilled, (state, action) => {
        state.loading = false;
        const { runId, key, points } = action.payload;
        if (!state.curves[runId]) state.curves[runId] = {};
        state.curves[runId][key] = points;
      })
      .addCase(fetchLossCurve.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message ?? 'Failed to fetch loss curve';
      })
      .addCase(fetchCompareMetrics.fulfilled, (state, action) => {
        state.compareData[action.payload.key] = action.payload.data;
      });
  },
});

export const { appendMetricPoint } = metricsSlice.actions;
export default metricsSlice.reducer;
