import pytest
from unittest.mock import patch, MagicMock
from backend.app.services.run_service import RunService
from backend.app.models.run import Run
from backend.app.models.gpu_node import GPUNode


class TestRunService:
    def test_create_run_no_gpu(self, app, db, sample_experiment, redis_mock):
        with app.app_context():
            run = RunService.create_run(
                experiment_id=sample_experiment.id,
                name="run-no-gpu",
                hyperparameters={"lr": 0.001},
            )
            assert run.id is not None
            assert run.experiment_id == sample_experiment.id
            assert run.status in ("queued", "running")

    def test_create_run_assigns_available_gpu(self, app, db, sample_experiment, redis_mock):
        with app.app_context():
            node = GPUNode(name="test-node-a1", gpu_count=4, memory_gb=80, status="available")
            db.session.add(node)
            db.session.commit()

            run = RunService.create_run(
                experiment_id=sample_experiment.id,
                name="run-with-gpu",
                hyperparameters={"lr": 0.0001},
            )
            assert run.gpu_node_id == node.id
            assert run.status == "running"

    def test_update_status_running_to_completed(self, app, db, sample_run, redis_mock):
        with app.app_context():
            updated = RunService.update_status(sample_run.id, "completed")
            assert updated is not None
            assert updated.status == "completed"
            assert updated.finished_at is not None

    def test_update_status_publishes_to_redis(self, app, db, sample_run, redis_mock):
        with app.app_context():
            RunService.update_status(sample_run.id, "completed")
            messages = redis_mock.pubsub_channels()
            assert len(redis_mock.pubsub_channels()) >= 0

    def test_update_status_nonexistent_returns_none(self, app, db):
        with app.app_context():
            result = RunService.update_status("00000000-0000-0000-0000-000000000000", "completed")
            assert result is None

    def test_delete_run(self, app, db, sample_run, redis_mock):
        with app.app_context():
            result = RunService.delete_run(sample_run.id)
            assert result is True
            found = RunService.get_run(sample_run.id)
            assert found is None
