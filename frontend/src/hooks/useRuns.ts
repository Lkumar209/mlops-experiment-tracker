import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import type { AppDispatch, RootState } from '../store';
import { fetchRuns } from '../store/runsSlice';
import type { RunStatus } from '../types/run';

export function useRuns(experimentId: string, status?: RunStatus) {
  const dispatch = useDispatch<AppDispatch>();
  const runs = useSelector((s: RootState) => s.runs.byExperiment[experimentId] || []);
  const loading = useSelector((s: RootState) => s.runs.loading);
  const meta = useSelector((s: RootState) => s.runs.meta[experimentId]);

  useEffect(() => {
    if (experimentId) {
      dispatch(fetchRuns({ experimentId, status }));
    }
  }, [dispatch, experimentId, status]);

  return { runs, loading, meta };
}
