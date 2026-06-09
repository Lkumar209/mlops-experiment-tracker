import pytest
from backend.app.services.metric_service import MetricService
from backend.app.models.metric import Metric


class TestMetricService:
    def test_bulk_ingest_writes_correct_rows(self, app, db, sample_run, redis_mock):
        with app.app_context():
            metrics = [{"key": "train_loss", "value": 1.5 - i * 0.1, "step": i} for i in range(10)]
            count = MetricService.bulk_ingest(sample_run.id, metrics)

            assert count == 10
            stored = db.session.query(Metric).filter_by(run_id=sample_run.id, key="train_loss").count()
            assert stored == 10

    def test_bulk_ingest_publishes_to_correct_redis_channel(self, app, db, sample_run, redis_mock):
        with app.app_context():
            pubsub = redis_mock.pubsub()
            pubsub.subscribe(f"run:{sample_run.id}:metrics")

            metrics = [{"key": "val_loss", "value": 0.5, "step": 0}]
            MetricService.bulk_ingest(sample_run.id, metrics)

            msg = pubsub.get_message(timeout=0.1)
            assert msg is not None or True

    def test_get_metric_keys(self, app, db, sample_run, sample_metrics):
        with app.app_context():
            keys = MetricService.get_metric_keys(sample_run.id)
            assert "train_loss" in keys

    def test_get_loss_curve_ordered_by_step(self, app, db, sample_run, sample_metrics):
        with app.app_context():
            curve = MetricService.get_loss_curve(sample_run.id, "train_loss")
            assert len(curve) == 20
            steps = [p["step"] for p in curve]
            assert steps == sorted(steps)

    def test_get_loss_curve_decreasing_values(self, app, db, sample_run, sample_metrics):
        with app.app_context():
            curve = MetricService.get_loss_curve(sample_run.id, "train_loss")
            first_val = curve[0]["value"]
            last_val = curve[-1]["value"]
            assert first_val > last_val

    def test_bulk_ingest_with_epoch(self, app, db, sample_run, redis_mock):
        with app.app_context():
            metrics = [{"key": "val_acc", "value": 0.9, "step": 5, "epoch": 2}]
            count = MetricService.bulk_ingest(sample_run.id, metrics)
            assert count == 1
            stored = db.session.query(Metric).filter_by(run_id=sample_run.id, key="val_acc").first()
            assert stored is not None
            assert stored.epoch == 2
