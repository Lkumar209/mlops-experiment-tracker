# API Reference

All routes require `X-API-Key` header. All responses use `{"data": ...}` or `{"data": ..., "meta": {...}}` for lists, and `{"error": {"code": "...", "message": "..."}}` for errors.

## Experiments

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/experiments | Paginated list. Params: `page`, `per_page`, `tags` (JSON), `sort_by` |
| POST | /api/v1/experiments | Create experiment. Body: `name`, `description`, `tags` |
| GET | /api/v1/experiments/{id} | Full detail with run list |
| PUT | /api/v1/experiments/{id} | Update name, description, tags |
| DELETE | /api/v1/experiments/{id} | Soft delete |

## Runs

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/experiments/{eid}/runs | Paginated runs. Params: `page`, `per_page`, `status` |
| POST | /api/v1/experiments/{eid}/runs | Create run, triggers GPU scheduling |
| GET | /api/v1/runs/{id} | Full run detail |
| PATCH | /api/v1/runs/{id}/status | Update status: queued/running/completed/failed |
| DELETE | /api/v1/runs/{id} | Delete run and cascade |

## Metrics

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/runs/{id}/metrics | Bulk ingest up to 1000 metric points |
| GET | /api/v1/runs/{id}/metrics | List metric keys for a run |
| GET | /api/v1/runs/{id}/metrics/{key} | Full loss curve ordered by step |
| GET | /api/v1/runs/{id}/metrics/compare | Multi-run comparison for a key. Param: `run_ids` (comma-separated), `key` |
| GET | /api/v1/runs/{id}/metrics/stream | SSE stream of new metric points |

## Artifacts

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/runs/{id}/artifacts | Register artifact |
| GET | /api/v1/runs/{id}/artifacts | List artifacts |
| GET | /api/v1/artifacts/{id} | Artifact detail |
| GET | /api/v1/artifacts/{id}/lineage | Full lineage DAG |

## GPU Nodes

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/gpu-nodes | List all nodes |
| GET | /api/v1/gpu-nodes/available | List available nodes |
| POST | /api/v1/gpu-nodes/{id}/heartbeat | Update heartbeat timestamp |

## Health

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Status with db/redis booleans |
| GET | /readiness | 200 if ready, 503 if not |
