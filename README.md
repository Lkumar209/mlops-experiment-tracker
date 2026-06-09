# MLOps Experiment Tracker

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-green?logo=flask)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?logo=typescript)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)
![Kubernetes](https://img.shields.io/badge/Kubernetes-1.29-326CE5?logo=kubernetes)
![Jenkins](https://img.shields.io/badge/Jenkins-CI%2FCD-D24939?logo=jenkins)

A production-grade MLOps Experiment Tracker for logging experiments, runs, metrics, and artifacts — with real-time loss curve streaming, GPU node scheduling, and a React/Redux dashboard.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        React/Redux Frontend                      │
│   Dashboard ─ ExperimentList ─ RunDetail ─ GPUMonitor           │
│   useMetricsStream (SSE) ─ Recharts live loss curves            │
└───────────────────────────────┬─────────────────────────────────┘
                                │ HTTP / SSE
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Flask REST API (Gunicorn 4 workers)        │
│  /api/v1/experiments  /api/v1/runs  /api/v1/metrics             │
│  /api/v1/artifacts    /api/v1/gpu-nodes  /health  /readiness    │
│  API Key middleware ─ Marshmallow validation ─ structlog         │
└──────────────┬────────────────────────────┬─────────────────────┘
               │ SQLAlchemy ORM             │ redis-py pub/sub
               ▼                            ▼
┌──────────────────────┐    ┌──────────────────────────────────────┐
│  PostgreSQL 16        │    │  Redis 7                              │
│  experiments          │    │  run:{id}:metrics  (pub/sub)         │
│  runs                 │    │  run:{id}:latest_metrics (hash)      │
│  metrics (4M+ rows)   │    │  gpu:queue (sorted set)              │
│  artifacts            │    │                                      │
│  gpu_nodes            │    │  Background Thread: metric_aggregator│
│  views:               │    │  Subscribes run:*:metrics            │
│  experiment_summary   │    │  Updates latest_metrics hash         │
│  run_metric_summary   │    └──────────────────────────────────────┘
└──────────────────────┘
               │
┌──────────────────────┐
│  GPU Nodes           │
│  Available/Busy/     │
│  Offline             │
│  Scheduled via       │
│  Redis sorted set    │
└──────────────────────┘

CI/CD: Jenkins → ruff/mypy/tsc → pytest/vitest → Docker build → kubectl rolling deploy
Infra: Kubernetes (2 backend replicas, 2 frontend replicas, Postgres StatefulSet, Redis)
```

## Quickstart

```bash
git clone https://github.com/Lkumar209/mlops-experiment-tracker.git
cd mlops-experiment-tracker
cp .env.example .env
make up        # docker compose up -d
make migrate   # flask db upgrade
make seed      # seed 50 experiments × 200 runs × 100 steps × 4 metrics
open http://localhost:3000
```

## API Usage

```bash
export API_KEY=dev-api-key
export BASE=http://localhost:5000/api/v1

# Create an experiment
curl -s -X POST $BASE/experiments \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name":"ResNet Ablation","tags":{"domain":"cv"}}' | jq .

# Create a run
curl -s -X POST $BASE/experiments/{experiment_id}/runs \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name":"run-lr-0001","hyperparameters":{"lr":0.001,"batch_size":32}}' | jq .

# Log metrics (bulk, up to 1000 per request)
curl -s -X POST $BASE/runs/{run_id}/metrics \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"metrics":[{"key":"train_loss","value":1.5,"step":0},{"key":"train_loss","value":1.2,"step":1}]}' | jq .

# Query a loss curve
curl -s $BASE/runs/{run_id}/metrics/train_loss \
  -H "X-API-Key: $API_KEY" | jq .

# Stream metrics in real-time (SSE)
curl -N "$BASE/runs/{run_id}/metrics/stream?api_key=$API_KEY"
```

## Kubernetes Deployment

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
# Create secrets first:
kubectl create secret generic mlops-secrets \
  --from-literal=DATABASE_URL=postgresql://... \
  --from-literal=REDIS_URL=redis://... \
  --from-literal=SECRET_KEY=prod-secret \
  --from-literal=API_KEY=prod-api-key \
  --from-literal=POSTGRES_USER=postgres \
  --from-literal=POSTGRES_PASSWORD=securepassword \
  -n mlops-tracker
kubectl apply -f k8s/
```

## Jenkins Setup

1. Install Docker Pipeline and Kubernetes CLI plugins.
2. Add credentials: `dockerhub-credentials` (Docker Hub), `kubeconfig` (kubeconfig file), `slack-webhook-url` (secret text).
3. Create a Multibranch Pipeline pointing to this repo.
4. Pushes to `main` trigger full CI → Docker build → Kubernetes rolling deploy with auto-rollback.

## Directory Structure

```
mlops-experiment-tracker/
├── backend/          Flask API, SQLAlchemy models, services, migrations
├── frontend/         React/Redux SPA with Recharts, Vite, TypeScript
├── k8s/              Kubernetes manifests (namespace, deployments, ingress)
├── jenkins/          Declarative Jenkins CI/CD pipeline
├── scripts/          Seed scripts (50 experiments × 200 runs × 4M metrics)
└── docs/             Architecture, API reference, deployment guides
```
