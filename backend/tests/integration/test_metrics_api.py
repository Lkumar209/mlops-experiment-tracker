import pytest


class TestMetricsAPI:
    def test_bulk_ingest_500_metrics(self, client, db, auth_headers, sample_run, redis_mock):
        metrics = [{"key": "train_loss", "value": 2.0 - i * 0.004, "step": i} for i in range(500)]
        resp = client.post(
            f"/api/v1/runs/{sample_run.id}/metrics",
            json={"metrics": metrics},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.get_json()["data"]["ingested"] == 500

    def test_bulk_ingest_exceeds_1000_limit(self, client, db, auth_headers, sample_run):
        metrics = [{"key": "loss", "value": 1.0, "step": i} for i in range(1001)]
        resp = client.post(
            f"/api/v1/runs/{sample_run.id}/metrics",
            json={"metrics": metrics},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_get_metric_keys(self, client, db, auth_headers, sample_run, sample_metrics):
        resp = client.get(f"/api/v1/runs/{sample_run.id}/metrics", headers=auth_headers)
        assert resp.status_code == 200
        keys = resp.get_json()["data"]
        assert "train_loss" in keys

    def test_get_loss_curve_ordered_by_step(self, client, db, auth_headers, sample_run, sample_metrics):
        resp = client.get(f"/api/v1/runs/{sample_run.id}/metrics/train_loss", headers=auth_headers)
        assert resp.status_code == 200
        curve = resp.get_json()["data"]
        assert len(curve) == 20
        steps = [p["step"] for p in curve]
        assert steps == sorted(steps)

    def test_get_loss_curve_nonexistent_key_returns_empty(self, client, db, auth_headers, sample_run):
        resp = client.get(f"/api/v1/runs/{sample_run.id}/metrics/nonexistent_key", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["data"] == []

    def test_bulk_ingest_invalid_run_returns_404(self, client, db, auth_headers):
        resp = client.post(
            "/api/v1/runs/00000000-0000-0000-0000-000000000000/metrics",
            json={"metrics": [{"key": "loss", "value": 1.0, "step": 0}]},
            headers=auth_headers,
        )
        assert resp.status_code == 404

    def test_compare_metrics(self, client, db, app, auth_headers, sample_run, sample_metrics, redis_mock):
        with app.app_context():
            from backend.app.models.run import Run
            from backend.app.extensions import db as _db

            run2 = Run(
                experiment_id=sample_run.experiment_id,
                name="compare-run",
                status="completed",
                hyperparameters={"lr": 0.01},
            )
            _db.session.add(run2)
            _db.session.commit()
            run2_id = run2.id

        metrics2 = [{"key": "train_loss", "value": 1.5 - i * 0.03, "step": i} for i in range(20)]
        client.post(f"/api/v1/runs/{run2_id}/metrics", json={"metrics": metrics2}, headers=auth_headers)

        resp = client.get(
            f"/api/v1/runs/{sample_run.id}/metrics/compare",
            query_string={"key": "train_loss", "run_ids": f"{sample_run.id},{run2_id}"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert sample_run.id in data
        assert run2_id in data
