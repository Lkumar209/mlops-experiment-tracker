import { configureStore } from '@reduxjs/toolkit';
import experimentsReducer from './experimentsSlice';
import runsReducer from './runsSlice';
import metricsReducer from './metricsSlice';
import gpuReducer from './gpuSlice';

export const store = configureStore({
  reducer: {
    experiments: experimentsReducer,
    runs: runsReducer,
    metrics: metricsReducer,
    gpu: gpuReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
