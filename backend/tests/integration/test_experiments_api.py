import json
import pytest


class TestExperimentsAPI:
    def test_list_experiments_requires_api_key(self, client):
        resp = client.get("/api/v1/experiments")
        assert resp.status_code == 401

    def test_list_experiments_empty(self, client, db, auth_headers):
        resp = client.get("/api/v1/experiments", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert "data" in data
        assert "meta" in data

    def test_create_experiment(self, client, db, auth_headers):
        resp = client.post(
            "/api/v1/experiments",
            json={"name": "Integration Test Exp", "description": "Test", "tags": {"domain": "cv"}},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["data"]["name"] == "Integration Test Exp"
        assert data["data"]["id"] is not None

    def test_create_duplicate_experiment_returns_409(self, client, db, auth_headers):
        client.post("/api/v1/experiments", json={"name": "Dup Exp"}, headers=auth_headers)
        resp = client.post("/api/v1/experiments", json={"name": "Dup Exp"}, headers=auth_headers)
        assert resp.status_code == 409

    def test_get_experiment(self, client, db, auth_headers, sample_experiment):
        resp = client.get(f"/api/v1/experiments/{sample_experiment.id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["data"]["id"] == sample_experiment.id

    def test_get_nonexistent_experiment_returns_404(self, client, db, auth_headers):
        resp = client.get("/api/v1/experiments/00000000-0000-0000-0000-000000000000", headers=auth_headers)
        assert resp.status_code == 404

    def test_update_experiment(self, client, db, auth_headers, sample_experiment):
        resp = client.put(
            f"/api/v1/experiments/{sample_experiment.id}",
            json={"description": "Updated description"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.get_json()["data"]["description"] == "Updated description"

    def test_delete_experiment(self, client, db, auth_headers, sample_experiment):
        resp = client.delete(f"/api/v1/experiments/{sample_experiment.id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["data"]["deleted"] is True

        resp2 = client.get(f"/api/v1/experiments/{sample_experiment.id}", headers=auth_headers)
        assert resp2.status_code == 404
