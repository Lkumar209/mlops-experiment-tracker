import pytest
from backend.app.models.gpu_node import GPUNode


class TestRunsAPI:
    def test_list_runs_requires_api_key(self, client, sample_experiment):
        resp = client.get(f"/api/v1/experiments/{sample_experiment.id}/runs")
        assert resp.status_code == 401

    def test_list_runs_empty(self, client, db, auth_headers, sample_experiment):
        resp = client.get(f"/api/v1/experiments/{sample_experiment.id}/runs", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["data"] == []

    def test_create_run(self, client, db, auth_headers, sample_experiment, redis_mock):
        resp = client.post(
            f"/api/v1/experiments/{sample_experiment.id}/runs",
            json={"name": "test-run-api", "hyperparameters": {"lr": 0.001, "batch": 32}},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["data"]["name"] == "test-run-api"
        assert data["data"]["experiment_id"] == sample_experiment.id

    def test_create_run_assigns_gpu_node(self, client, db, app, auth_headers, sample_experiment, redis_mock):
        with app.app_context():
            node = GPUNode(name="api-test-node", gpu_count=8, memory_gb=40, status="available")
            db.session.add(node)
            db.session.commit()

        resp = client.post(
            f"/api/v1/experiments/{sample_experiment.id}/runs",
            json={"name": "gpu-run"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["data"]["gpu_node_id"] is not None
        assert data["data"]["status"] == "running"

    def test_update_run_status(self, client, db, auth_headers, sample_run, redis_mock):
        resp = client.patch(
            f"/api/v1/runs/{sample_run.id}/status",
            json={"status": "completed"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.get_json()["data"]["status"] == "completed"

    def test_update_run_status_invalid_value(self, client, db, auth_headers, sample_run):
        resp = client.patch(
            f"/api/v1/runs/{sample_run.id}/status",
            json={"status": "invalid_status"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_delete_run(self, client, db, auth_headers, sample_run, redis_mock):
        resp = client.delete(f"/api/v1/runs/{sample_run.id}", headers=auth_headers)
        assert resp.status_code == 200

        resp2 = client.get(f"/api/v1/runs/{sample_run.id}", headers=auth_headers)
        assert resp2.status_code == 404
