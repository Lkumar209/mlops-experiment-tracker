# Architecture

## Data Flow

```
React/Redux Dashboard
  → Axios apiClient (X-API-Key header)
  → Flask REST API (Gunicorn 4 workers, port 5000)
  → SQLAlchemy ORM
  → PostgreSQL 16 (experiments, runs, metrics, artifacts, gpu_nodes)

Metric Logging (real-time path):
  POST /api/v1/runs/{run_id}/metrics
  → MetricService.bulk_ingest()
  → INSERT INTO metrics (executemany via SQLAlchemy text())
  → redis.pipeline().publish(run:{id}:metrics, JSON) × N
  → Background Thread (metric_aggregator.py)
      subscribes psubscribe("run:*:metrics")
      updates run:{id}:latest_metrics hash
  → SSE endpoint GET /api/v1/runs/{run_id}/metrics/stream
      polls pubsub.get_message()
      yields "data: {...}\n\n"
  → useMetricsStream hook (EventSource)
      dispatches appendMetricPoint to Redux store
  → LossCurve component (Recharts LineChart, isAnimationActive=false)
      re-renders on new store data
```

## Why PostgreSQL JSONB for Hyperparameters and Tags

Hyperparameters are highly variable across experiments — ResNet ablations have different keys than BERT fine-tunes. A normalized schema would require a `hyperparameter_definitions` table, `run_hyperparameters` junction table, and complex JOINs to reconstruct a run's full config. JSONB stores the entire dict atomically, lets SQLAlchemy map it directly to Python dicts, and supports GIN-indexed containment queries (`@>`) for tag filtering (e.g., `WHERE tags @> '{"domain":"cv"}'::jsonb`). The query patterns (fetch one run's hyperparameters, filter experiments by tag) align well with JSONB's strengths.

## SSE Streaming Pipeline

1. **Ingest**: `POST /runs/{id}/metrics` → `MetricService.bulk_ingest()` publishes to Redis channel `run:{id}:metrics`.
2. **Aggregator**: `metric_aggregator.py` runs as a daemon thread, `psubscribe("run:*:metrics")`, and updates `run:{id}:latest_metrics` hash with the latest value per key — so the SSE endpoint can always serve the current state without hitting Postgres.
3. **SSE Endpoint**: `GET /runs/{id}/metrics/stream` is a Flask streaming response (`stream_with_context`). It subscribes to the Redis pub/sub channel and yields each message as `data: {json}\n\n` with a heartbeat comment on timeout. `Content-Type: text/event-stream`, `Cache-Control: no-cache`.
4. **React Hook**: `useMetricsStream(runId, enabled)` opens an `EventSource`, parses each message, and dispatches `appendMetricPoint` to the Redux `metricsSlice`. The slice pushes the point into `state.curves[runId][key]`.
5. **Chart**: `LossCurve` renders a `Recharts LineChart` subscribed to Redux state. With `isAnimationActive=false`, new points append smoothly without re-running transitions.

## GPU Scheduling Algorithm

The scheduler uses a **priority queue** in a Redis sorted set (`gpu:queue`, score = timestamp) and a database-level `SELECT FOR UPDATE SKIP LOCKED` to avoid double-assignment under concurrent requests.

```
schedule_run(run_id):
  SELECT FROM gpu_nodes WHERE status='available' ORDER BY memory_gb DESC
    FOR UPDATE SKIP LOCKED LIMIT 1
  if found:
    node.status = 'busy', node.current_run_id = run_id → flush
    return node.id
  else:
    ZADD gpu:queue {run_id: time.time()}
    return None  → run stays 'queued'

release_node(node_id):
  SELECT FROM gpu_nodes WHERE id=node_id FOR UPDATE
  next_run = ZRANGE gpu:queue 0 0  (lowest score = oldest)
  if next_run:
    ZREM gpu:queue next_run
    node.current_run_id = next_run, run.status = 'running' → commit
  else:
    node.status = 'available', node.current_run_id = None → commit
```

`release_node` is called automatically when a run transitions to `completed` or `failed`.

## Kubernetes Zero-Downtime Rollout

Both `backend` and `frontend` Deployments use `RollingUpdate` with `maxUnavailable: 0` and `maxSurge: 1`. This guarantees at least 2 replicas are always serving traffic during a deploy. The backend's `readinessProbe` (GET /readiness every 5s, failureThreshold=2) ensures the new pod must pass both database and Redis connectivity checks before old pods are terminated.

The Jenkins pipeline:
1. `kubectl set image` on both deployments
2. `kubectl rollout status --timeout=120s` for each
3. If either exits non-zero → `kubectl rollout undo` on both, pipeline fails with Slack alert
