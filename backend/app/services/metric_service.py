import json
import uuid
from datetime import datetime, timezone

import structlog
from sqlalchemy import text

from ..extensions import db, redis_client
from ..models.metric import Metric

log = structlog.get_logger()


class MetricService:
    @staticmethod
    def bulk_ingest(run_id: str, metrics: list[dict]) -> int:
        now = datetime.now(timezone.utc)
        rows = [
            {
                "id": str(uuid.uuid4()),
                "run_id": run_id,
                "key": m["key"],
                "value": m["value"],
                "step": m["step"],
                "epoch": m.get("epoch"),
                "logged_at": now,
            }
            for m in metrics
        ]

        db.session.execute(
            text(
                "INSERT INTO metrics (id, run_id, key, value, step, epoch, logged_at) "
                "VALUES (:id, :run_id, :key, :value, :step, :epoch, :logged_at)"
            ),
            rows,
        )
        db.session.commit()

        if redis_client:
            pipe = redis_client.pipeline()
            for row in rows:
                payload = json.dumps({"run_id": run_id, "key": row["key"], "value": row["value"], "step": row["step"], "logged_at": row["logged_at"].isoformat()})
                pipe.publish(f"run:{run_id}:metrics", payload)
            pipe.execute()

        log.info("metrics_ingested", run_id=run_id, count=len(rows))
        return len(rows)

    @staticmethod
    def get_metric_keys(run_id: str) -> list[str]:
        result = db.session.execute(
            text("SELECT DISTINCT key FROM metrics WHERE run_id = :run_id ORDER BY key"),
            {"run_id": run_id},
        )
        return [row[0] for row in result]

    @staticmethod
    def get_loss_curve(run_id: str, key: str) -> list[dict]:
        result = db.session.execute(
            text(
                "SELECT step, value, logged_at FROM metrics "
                "WHERE run_id = :run_id AND key = :key "
                "ORDER BY step ASC"
            ),
            {"run_id": run_id, "key": key},
        )
        return [{"step": row[0], "value": row[1], "logged_at": row[2].isoformat()} for row in result]

    @staticmethod
    def get_compare_metrics(run_ids: list[str], key: str) -> dict[str, list[dict]]:
        result = {}
        for run_id in run_ids:
            result[run_id] = MetricService.get_loss_curve(run_id, key)
        return result
