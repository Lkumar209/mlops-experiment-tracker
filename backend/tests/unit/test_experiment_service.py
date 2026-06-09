import pytest
from backend.app.services.experiment_service import ExperimentService
from backend.app.models.experiment import Experiment


class TestExperimentService:
    def test_create_experiment(self, app, db):
        with app.app_context():
            exp = ExperimentService.create_experiment(
                name="CV Benchmark",
                description="Benchmark run",
                tags={"domain": "cv"},
            )
            assert exp.id is not None
            assert exp.name == "CV Benchmark"
            assert exp.tags == {"domain": "cv"}

    def test_create_duplicate_name_raises(self, app, db):
        with app.app_context():
            ExperimentService.create_experiment(name="Unique Exp", description=None, tags={})
            with pytest.raises(ValueError, match="already exists"):
                ExperimentService.create_experiment(name="Unique Exp", description=None, tags={})

    def test_list_experiments_with_tag_filter(self, app, db):
        with app.app_context():
            ExperimentService.create_experiment(name="NLP Exp", description=None, tags={"domain": "nlp"})
            ExperimentService.create_experiment(name="CV Exp 2", description=None, tags={"domain": "cv"})

            results, total = ExperimentService.list_experiments(tags_filter={"domain": "nlp"})
            assert all(e["tags"].get("domain") == "nlp" for e in results)

    def test_list_experiments_pagination(self, app, db):
        with app.app_context():
            for i in range(5):
                ExperimentService.create_experiment(name=f"Paged Exp {i}", description=None, tags={})

            page1, total = ExperimentService.list_experiments(page=1, per_page=3)
            page2, _ = ExperimentService.list_experiments(page=2, per_page=3)
            assert len(page1) <= 3
            assert total >= 5

    def test_delete_experiment_soft_deletes(self, app, db, sample_experiment):
        with app.app_context():
            result = ExperimentService.delete_experiment(sample_experiment.id)
            assert result is True
            found = ExperimentService.get_experiment(sample_experiment.id)
            assert found is None

    def test_delete_nonexistent_returns_false(self, app, db):
        with app.app_context():
            result = ExperimentService.delete_experiment("00000000-0000-0000-0000-000000000000")
            assert result is False

    def test_update_experiment(self, app, db, sample_experiment):
        with app.app_context():
            updated = ExperimentService.update_experiment(
                sample_experiment.id, {"description": "Updated", "tags": {"domain": "nlp"}}
            )
            assert updated is not None
            assert updated.description == "Updated"
            assert updated.tags == {"domain": "nlp"}
