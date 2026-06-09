import json
from datetime import datetime, timezone

import structlog

from ..extensions import db, redis_client
from ..models.run import Run
from .gpu_scheduler import GPUScheduler

log = structlog.get_logger()


class RunService:
    @staticmethod
    def list_runs(experiment_id: str, page: int = 1, per_page: int = 20, status: str | None = None) -> tuple[list[dict], int]:
        query = db.session.query(Run).filter_by(experiment_id=experiment_id)
        if status:
            query = query.filter_by(status=status)

        total = query.count()
        runs = query.order_by(Run.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
        return [r.to_dict() for r in runs], total

    @staticmethod
    def create_run(experiment_id: str, name: str, hyperparameters: dict) -> Run:
        run = Run(experiment_id=experiment_id, name=name, hyperparameters=hyperparameters)
        db.session.add(run)
        db.session.flush()

        node_id = GPUScheduler.schedule_run(run.id)
        if node_id:
            run.gpu_node_id = node_id
            run.status = "running"
            run.started_at = datetime.now(timezone.utc)

        db.session.commit()
        log.info("run_created", run_id=run.id, experiment_id=experiment_id, gpu_node_id=node_id)
        return run

    @staticmethod
    def get_run(run_id: str) -> Run | None:
        return db.session.query(Run).filter_by(id=run_id).first()

    @staticmethod
    def update_status(run_id: str, status: str) -> Run | None:
        run = RunService.get_run(run_id)
        if not run:
            return None

        old_status = run.status
        run.status = status

        if status == "running" and not run.started_at:
            run.started_at = datetime.now(timezone.utc)
        elif status in ("completed", "failed"):
            run.finished_at = datetime.now(timezone.utc)
            if run.gpu_node_id:
                GPUScheduler.release_node(run.gpu_node_id)

        db.session.commit()

        if redis_client:
            redis_client.publish(
                f"run:{run_id}:status",
                json.dumps({"run_id": run_id, "status": status, "previous_status": old_status}),
            )

        log.info("run_status_updated", run_id=run_id, status=status)
        return run

    @staticmethod
    def delete_run(run_id: str) -> bool:
        run = RunService.get_run(run_id)
        if not run:
            return False

        if run.gpu_node_id and run.status in ("running", "queued"):
            GPUScheduler.release_node(run.gpu_node_id)

        db.session.delete(run)
        db.session.commit()
        log.info("run_deleted", run_id=run_id)
        return True
