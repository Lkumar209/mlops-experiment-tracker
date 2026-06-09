import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { experimentsApi } from '../api/experiments';
import type { Experiment } from '../types/experiment';

interface ExperimentsState {
  items: Experiment[];
  selected: Experiment | null;
  loading: boolean;
  error: string | null;
  meta: { page: number; total: number; per_page: number };
}

const initialState: ExperimentsState = {
  items: [],
  selected: null,
  loading: false,
  error: null,
  meta: { page: 1, total: 0, per_page: 20 },
};

export const fetchExperiments = createAsyncThunk(
  'experiments/fetchAll',
  async (params: { page?: number; tags?: string; sort_by?: string } = {}) => {
    return await experimentsApi.list(params);
  }
);

export const fetchExperiment = createAsyncThunk(
  'experiments/fetchOne',
  async (id: string) => {
    return await experimentsApi.get(id);
  }
);

export const createExperiment = createAsyncThunk(
  'experiments/create',
  async (payload: { name: string; description?: string; tags?: Record<string, string> }) => {
    return await experimentsApi.create(payload);
  }
);

export const updateExperiment = createAsyncThunk(
  'experiments/update',
  async ({ id, payload }: { id: string; payload: { name?: string; description?: string; tags?: Record<string, string> } }) => {
    return await experimentsApi.update(id, payload);
  }
);

export const deleteExperiment = createAsyncThunk(
  'experiments/delete',
  async (id: string) => {
    await experimentsApi.delete(id);
    return id;
  }
);

const experimentsSlice = createSlice({
  name: 'experiments',
  initialState,
  reducers: {
    clearSelected: (state) => {
      state.selected = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchExperiments.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchExperiments.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload.data;
        state.meta = { page: action.payload.meta.page, total: action.payload.meta.total, per_page: action.payload.meta.per_page };
      })
      .addCase(fetchExperiments.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message ?? 'Failed to fetch experiments';
      })
      .addCase(fetchExperiment.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchExperiment.fulfilled, (state, action) => {
        state.loading = false;
        state.selected = action.payload;
      })
      .addCase(fetchExperiment.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message ?? 'Failed to fetch experiment';
      })
      .addCase(createExperiment.fulfilled, (state, action) => {
        state.items.unshift(action.payload);
        state.meta.total += 1;
      })
      .addCase(updateExperiment.fulfilled, (state, action) => {
        const idx = state.items.findIndex((e) => e.id === action.payload.id);
        if (idx !== -1) state.items[idx] = action.payload;
        if (state.selected?.id === action.payload.id) state.selected = action.payload;
      })
      .addCase(deleteExperiment.fulfilled, (state, action) => {
        state.items = state.items.filter((e) => e.id !== action.payload);
        if (state.selected?.id === action.payload) state.selected = null;
        state.meta.total = Math.max(0, state.meta.total - 1);
      });
  },
});

export const { clearSelected } = experimentsSlice.actions;
export default experimentsSlice.reducer;
