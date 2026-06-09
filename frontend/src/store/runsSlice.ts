import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { runsApi } from '../api/runs';
import type { Run, RunStatus } from '../types/run';

interface RunsState {
  byExperiment: Record<string, Run[]>;
  selected: Run | null;
  loading: boolean;
  error: string | null;
  meta: Record<string, { page: number; total: number }>;
}

const initialState: RunsState = {
  byExperiment: {},
  selected: null,
  loading: false,
  error: null,
  meta: {},
};

export const fetchRuns = createAsyncThunk(
  'runs/fetchAll',
  async ({ experimentId, page, status }: { experimentId: string; page?: number; status?: RunStatus }) => {
    const response = await runsApi.list(experimentId, { page, status });
    return { experimentId, ...response };
  }
);

export const fetchRun = createAsyncThunk('runs/fetchOne', async (runId: string) => {
  return await runsApi.get(runId);
});

export const createRun = createAsyncThunk(
  'runs/create',
  async ({ experimentId, payload }: { experimentId: string; payload: { name: string; hyperparameters?: Record<string, unknown> } }) => {
    const run = await runsApi.create(experimentId, payload);
    return { experimentId, run };
  }
);

export const updateRunStatus = createAsyncThunk(
  'runs/updateStatus',
  async ({ runId, status, experimentId }: { runId: string; status: RunStatus; experimentId: string }, { rejectWithValue }) => {
    try {
      const run = await runsApi.updateStatus(runId, status);
      return { run, experimentId };
    } catch (error) {
      return rejectWithValue({ runId, experimentId, error: String(error) });
    }
  }
);

const runsSlice = createSlice({
  name: 'runs',
  initialState,
  reducers: {
    clearSelected: (state) => {
      state.selected = null;
    },
    optimisticStatusUpdate: (state, action: { payload: { runId: string; experimentId: string; status: RunStatus } }) => {
      const runs = state.byExperiment[action.payload.experimentId] || [];
      const run = runs.find((r) => r.id === action.payload.runId);
      if (run) run.status = action.payload.status;
      if (state.selected?.id === action.payload.runId) state.selected.status = action.payload.status;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchRuns.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchRuns.fulfilled, (state, action) => {
        state.loading = false;
        state.byExperiment[action.payload.experimentId] = action.payload.data;
        state.meta[action.payload.experimentId] = { page: action.payload.meta.page, total: action.payload.meta.total };
      })
      .addCase(fetchRuns.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message ?? 'Failed to fetch runs';
      })
      .addCase(fetchRun.fulfilled, (state, action) => {
        state.selected = action.payload;
      })
      .addCase(createRun.fulfilled, (state, action) => {
        const { experimentId, run } = action.payload;
        if (!state.byExperiment[experimentId]) state.byExperiment[experimentId] = [];
        state.byExperiment[experimentId].unshift(run);
        if (state.meta[experimentId]) state.meta[experimentId].total += 1;
      })
      .addCase(updateRunStatus.fulfilled, (state, action) => {
        const { run, experimentId } = action.payload;
        const runs = state.byExperiment[experimentId] || [];
        const idx = runs.findIndex((r) => r.id === run.id);
        if (idx !== -1) runs[idx] = run;
        if (state.selected?.id === run.id) state.selected = run;
      })
      .addCase(updateRunStatus.rejected, (state, action) => {
        const payload = action.payload as { runId: string; experimentId: string } | undefined;
        if (payload) {
          state.error = 'Failed to update run status';
        }
      });
  },
});

export const { clearSelected, optimisticStatusUpdate } = runsSlice.actions;
export default runsSlice.reducer;
