#!/usr/bin/env python3
"""Seed 200 runs per experiment with randomized hyperparameters."""
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app
from backend.app.extensions import db
from backend.app.models.experiment import Experiment
from backend.app.models.run import Run
from backend.app.models.gpu_node import GPUNode

OPTIMIZERS = ["adam", "sgd", "adamw", "rmsprop", "adagrad"]
SCHEDULERS = ["cosine", "linear", "step", "exponential", "constant"]
RUNS_PER_EXPERIMENT = 200


def random_hyperparams() -> dict:
    return {
        "learning_rate": round(random.choice([1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2]), 6),
        "batch_size": random.choice([8, 16, 32, 64, 128, 256]),
        "optimizer": random.choice(OPTIMIZERS),
        "dropout": round(random.uniform(0.0, 0.5), 2),
        "weight_decay": round(random.choice([0.0, 1e-5, 1e-4, 1e-3, 1e-2]), 6),
        "epochs": random.choice([5, 10, 20, 50, 100]),
        "scheduler": random.choice(SCHEDULERS),
        "warmup_steps": random.choice([0, 100, 500, 1000]),
        "hidden_size": random.choice([128, 256, 512, 768, 1024]),
    }


def seed():
    app = create_app()
    with app.app_context():
        experiments = db.session.query(Experiment).filter(Experiment.deleted_at.is_(None)).all()
        if not experiments:
            print("No experiments found. Run seed_experiments.py first.")
            return

        nodes = db.session.query(GPUNode).all()

        for exp in experiments:
            existing_count = db.session.query(Run).filter_by(experiment_id=exp.id).count()
            needed = RUNS_PER_EXPERIMENT - existing_count
            if needed <= 0:
                print(f"  Skipping {exp.name}: already has {existing_count} runs")
                continue

            print(f"  Seeding {needed} runs for: {exp.name}")
            statuses = ["completed"] * 140 + ["failed"] * 30 + ["running"] * 20 + ["queued"] * 10

            for i in range(needed):
                status = random.choice(statuses)
                node = random.choice(nodes) if nodes and status in ("running", "completed") else None
                run = Run(
                    experiment_id=exp.id,
                    name=f"run-{exp.name[:20]}-{i:04d}",
                    status=status,
                    hyperparameters=random_hyperparams(),
                    gpu_node_id=node.id if node else None,
                )
                db.session.add(run)

            db.session.flush()

        db.session.commit()
        total = db.session.query(Run).count()
        print(f"Seeded runs. Total: {total}")


if __name__ == "__main__":
    seed()
