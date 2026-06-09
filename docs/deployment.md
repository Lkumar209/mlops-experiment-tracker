# Deployment Guide

## Local Development

```bash
cp .env.example .env
make up      # starts postgres, redis, backend, frontend
make migrate # flask db upgrade
make seed    # 4M+ metric rows
open http://localhost:3000
```

## Production (Kubernetes)

### Prerequisites
- kubectl configured for your cluster
- Nginx Ingress Controller installed
- Docker Hub account (lkumar209)

### Steps

```bash
# 1. Apply namespace and config
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml

# 2. Create secrets
kubectl create secret generic mlops-secrets \
  --from-literal=DATABASE_URL=postgresql://... \
  --from-literal=REDIS_URL=redis://... \
  --from-literal=SECRET_KEY=$(openssl rand -hex 32) \
  --from-literal=API_KEY=$(openssl rand -hex 16) \
  --from-literal=POSTGRES_USER=postgres \
  --from-literal=POSTGRES_PASSWORD=$(openssl rand -hex 16) \
  -n mlops-tracker

# 3. Deploy all resources
kubectl apply -f k8s/

# 4. Verify rollout
kubectl rollout status deployment/backend -n mlops-tracker
kubectl rollout status deployment/frontend -n mlops-tracker

# 5. Check health
kubectl run -it --rm check --image=curlimages/curl --restart=Never -- \
  curl http://backend.mlops-tracker.svc.cluster.local:5000/health
```

### Rolling Update

```bash
# Jenkins handles this automatically on push to main.
# Manual trigger:
kubectl set image deployment/backend backend=lkumar209/mlops-tracker-backend:NEW_SHA -n mlops-tracker
kubectl rollout status deployment/backend --timeout=120s -n mlops-tracker
# Rollback if needed:
kubectl rollout undo deployment/backend -n mlops-tracker
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | — |
| `REDIS_URL` | Redis connection string | — |
| `SECRET_KEY` | Flask secret key | — |
| `API_KEY` | API authentication key | — |
| `FLASK_ENV` | `development` or `production` | `development` |
| `VITE_API_BASE_URL` | Frontend API base URL | `http://localhost:5000` |
