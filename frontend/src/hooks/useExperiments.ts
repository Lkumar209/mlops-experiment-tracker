import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import type { AppDispatch, RootState } from '../store';
import { fetchExperiments } from '../store/experimentsSlice';

export function useExperiments(params: { page?: number; tags?: string; sort_by?: string } = {}) {
  const dispatch = useDispatch<AppDispatch>();
  const { items, loading, error, meta } = useSelector((s: RootState) => s.experiments);

  useEffect(() => {
    dispatch(fetchExperiments(params));
  }, [dispatch, params.page, params.tags, params.sort_by]);

  return { experiments: items, loading, error, meta };
}
