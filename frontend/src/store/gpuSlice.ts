import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { apiClient } from '../api/client';

export interface GPUNode {
  id: string;
  name: string;
  gpu_count: number;
  memory_gb: number;
  status: 'available' | 'busy' | 'offline';
  current_run_id: string | null;
  last_heartbeat: string | null;
}

interface GPUState {
  nodes: GPUNode[];
  loading: boolean;
  error: string | null;
}

const initialState: GPUState = {
  nodes: [],
  loading: false,
  error: null,
};

export const fetchGPUNodes = createAsyncThunk('gpu/fetchNodes', async () => {
  const response = await apiClient.get<{ data: GPUNode[]; meta: { total: number } }>('/gpu-nodes');
  return response.data.data;
});

const gpuSlice = createSlice({
  name: 'gpu',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchGPUNodes.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchGPUNodes.fulfilled, (state, action) => {
        state.loading = false;
        state.nodes = action.payload;
      })
      .addCase(fetchGPUNodes.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message ?? 'Failed to fetch GPU nodes';
      });
  },
});

export default gpuSlice.reducer;
