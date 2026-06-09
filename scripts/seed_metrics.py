#!/usr/bin/env python3
"""Seed metrics and artifacts for all completed/running runs."""
import math
import random
import uuid
import sys
import os
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app
from backend.app.extensions import db
from backend.app.models.run import Run
from backend.app.models.metric import Metric
from backend.app.models.artifact import Artifact

STEPS = 100
METRIC_KEYS = ["train_loss", "val_loss", "train_acc", "val_acc"]
BATCH_SIZE = 10000


def loss_curve(step: int, total: int, base: float = 2.5, floor: float = 0.05) -> float:
    t = step / total
    return floor + (base - floor) * math.exp(-4 * t) + random.gauss(0, 0.02)


def acc_curve(step: int, total: int, ceiling: float = 0.97, floor: float = 0.5) -> float:
    t = step / total
    return floor + (ceiling - floor) * (1 - math.exp(-4 * t)) + random.gauss(0, 0.01)


def seed():
    app = create_app()
    with app.app_context():
        runs = db.session.query(Run).filter(Run.status.in_(["completed", "running"])).all()
        print(f"Seeding metrics for {len(runs)} runs ({len(runs) * STEPS * len(METRIC_KEYS):,} metric rows total)...")

        batch = []
        artifact_batch = []

        for run_idx, run in enumerate(runs):
            existing = db.session.query(Metric).filter_by(run_id=run.id).count()
            if existing > 0:
                continue

            base_time = run.started_at or datetime.now(timezone.utc)
            train_base = random.uniform(1.5, 3.0)
            val_base = train_base + random.uniform(0.1, 0.3)

            for step in range(STEPS):
                logged_at = base_time + timedelta(seconds=step * 30)
                for key in METRIC_KEYS:
                    if "loss" in key:
                        val = loss_curve(step, STEPS, base=train_base if "train" in key else val_base)
                    else:
                        val = acc_curve(step, STEPS)

                    batch.append({
                        "id": str(uuid.uuid4()),
                        "run_id": run.id,
                        "key": key,
                        "value": round(max(0.0, val), 6),
                        "step": step,
                        "epoch": step // 10,
                        "logged_at": logged_at,
                    })

            prev_artifact_id = None
            for art_type, art_name in [("checkpoint", "initial_checkpoint"), ("checkpoint", "best_checkpoint"), ("model", "final_model")]:
                art_id = str(uuid.uuid4())
                artifact_batch.append(Artifact(
                    id=art_id,
                    run_id=run.id,
                    name=art_name,
                    artifact_type=art_type,
                    uri=f"s3://mlops-artifacts/{run.id}/{art_name}.pt",
                    size_bytes=random.randint(50_000_000, 2_000_000_000),
                    checksum=uuid.uuid4().hex,
                    parent_artifact_id=prev_artifact_id,
                ))
                prev_artifact_id = art_id

            if len(batch) >= BATCH_SIZE:
                from sqlalchemy import text
                db.session.execute(
                    text("INSERT INTO metrics (id, run_id, key, value, step, epoch, logged_at) VALUES (:id, :run_id, :key, :value, :step, :epoch, :logged_at)"),
                    batch,
                )
                db.session.commit()
                print(f"  Committed {len(batch):,} metric rows (run {run_idx + 1}/{len(runs)})")
                batch = []

        if batch:
            from sqlalchemy import text
            db.session.execute(
                text("INSERT INTO metrics (id, run_id, key, value, step, epoch, logged_at) VALUES (:id, :run_id, :key, :value, :step, :epoch, :logged_at)"),
                batch,
            )
            db.session.commit()

        if artifact_batch:
            db.session.bulk_save_objects(artifact_batch)
            db.session.commit()

        total_metrics = db.session.query(Metric).count()
        total_artifacts = db.session.query(Artifact).count()
        print(f"Done. Total metrics: {total_metrics:,}, artifacts: {total_artifacts:,}")


if __name__ == "__main__":
    seed()
