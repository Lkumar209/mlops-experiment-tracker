import pytest
import fakeredis
from unittest.mock import patch

from backend.app import create_app
from backend.app.extensions import db as _db


@pytest.fixture(scope="session")
def app():
    test_config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "TESTING": True,
        "API_KEY": "test-api-key",
        "SECRET_KEY": "test-secret",
        "REDIS_URL": "redis://localhost:6379",
    }
    with patch("backend.app.extensions.init_redis"):
        application = create_app(test_config)

    with application.app_context():
        _db.create_all()
        yield application
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    with app.app_context():
        yield _db
        _db.session.rollback()
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


@pytest.fixture
def redis_mock():
    fake = fakeredis.FakeRedis(decode_responses=True)
    with patch("backend.app.extensions.redis_client", fake):
        with patch("backend.app.services.metric_service.redis_client", fake):
            with patch("backend.app.services.run_service.redis_client", fake):
                with patch("backend.app.services.gpu_scheduler.redis_client", fake):
                    yield fake


@pytest.fixture
def auth_headers():
    return {"X-API-Key": "test-api-key"}


@pytest.fixture
def sample_experiment(db):
    from backend.app.models.experiment import Experiment

    exp = Experiment(name="Test Experiment", description="A test experiment", tags={"domain": "cv"})
    db.session.add(exp)
    db.session.commit()
    return exp


@pytest.fixture
def sample_run(db, sample_experiment):
    from backend.app.models.run import Run

    run = Run(
        experiment_id=sample_experiment.id,
        name="test-run-001",
        status="running",
        hyperparameters={"learning_rate": 0.001, "batch_size": 32},
    )
    db.session.add(run)
    db.session.commit()
    return run


@pytest.fixture
def sample_metrics(db, sample_run):
    from backend.app.models.metric import Metric
    from datetime import datetime, timezone

    metrics = [
        Metric(run_id=sample_run.id, key="train_loss", value=2.0 - i * 0.05, step=i)
        for i in range(20)
    ]
    db.session.bulk_save_objects(metrics)
    db.session.commit()
    return metrics
