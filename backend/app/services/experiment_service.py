from datetime import datetime, timezone

import structlog
from sqlalchemy import text

from ..extensions import db
from ..models.experiment import Experiment

log = structlog.get_logger()


class ExperimentService:
    @staticmethod
    def list_experiments(page: int = 1, per_page: int = 20, tags_filter: dict | None = None, sort_by: str = "created_at") -> tuple[list[dict], int]:
        query = db.session.query(Experiment).filter(Experiment.deleted_at.is_(None))

        if tags_filter:
            query = query.filter(Experiment.tags.op("@>")(tags_filter))

        total = query.count()

        if sort_by == "total_runs":
            subq = (
                db.session.execute(
                    text("SELECT id, COUNT(r.id) AS total_runs FROM experiments e LEFT JOIN runs r ON r.experiment_id = e.id GROUP BY e.id")
                )
            )
            run_counts = {row[0]: row[1] for row in subq}
            experiments = query.all()
            experiments.sort(key=lambda e: run_counts.get(e.id, 0), reverse=True)
            start = (page - 1) * per_page
            experiments = experiments[start : start + per_page]
        else:
            experiments = query.order_by(Experiment.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

        return [e.to_dict() for e in experiments], total

    @staticmethod
    def create_experiment(name: str, description: str | None, tags: dict) -> Experiment:
        existing = db.session.query(Experiment).filter_by(name=name).filter(Experiment.deleted_at.is_(None)).first()
        if existing:
            raise ValueError(f"Experiment with name '{name}' already exists")

        experiment = Experiment(name=name, description=description, tags=tags)
        db.session.add(experiment)
        db.session.commit()
        log.info("experiment_created", experiment_id=experiment.id, name=name)
        return experiment

    @staticmethod
    def get_experiment(experiment_id: str) -> Experiment | None:
        return db.session.query(Experiment).filter_by(id=experiment_id).filter(Experiment.deleted_at.is_(None)).first()

    @staticmethod
    def update_experiment(experiment_id: str, data: dict) -> Experiment | None:
        experiment = ExperimentService.get_experiment(experiment_id)
        if not experiment:
            return None

        if "name" in data and data["name"] != experiment.name:
            existing = db.session.query(Experiment).filter_by(name=data["name"]).filter(Experiment.deleted_at.is_(None)).first()
            if existing:
                raise ValueError(f"Experiment with name '{data['name']}' already exists")
            experiment.name = data["name"]

        if "description" in data:
            experiment.description = data["description"]
        if "tags" in data:
            experiment.tags = data["tags"]

        experiment.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        log.info("experiment_updated", experiment_id=experiment_id)
        return experiment

    @staticmethod
    def delete_experiment(experiment_id: str) -> bool:
        experiment = ExperimentService.get_experiment(experiment_id)
        if not experiment:
            return False

        experiment.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        log.info("experiment_deleted", experiment_id=experiment_id)
        return True
