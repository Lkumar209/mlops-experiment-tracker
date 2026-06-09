"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-06-08 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE TYPE run_status AS ENUM ('queued', 'running', 'completed', 'failed')")
    op.execute("CREATE TYPE artifact_type AS ENUM ('model', 'dataset', 'checkpoint', 'log')")
    op.execute("CREATE TYPE gpu_node_status AS ENUM ('available', 'busy', 'offline')")

    op.create_table(
        "experiments",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("tags", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_experiments_name", "experiments", ["name"])
    op.create_index("ix_experiments_tags", "experiments", ["tags"], postgresql_using="gin")

    op.create_table(
        "gpu_nodes",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("gpu_count", sa.Integer, nullable=False, server_default="1"),
        sa.Column("memory_gb", sa.Integer, nullable=False),
        sa.Column("status", sa.Enum("available", "busy", "offline", name="gpu_node_status"), nullable=False, server_default="available"),
        sa.Column("current_run_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("last_heartbeat", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "runs",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("experiment_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("experiments.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("status", sa.Enum("queued", "running", "completed", "failed", name="run_status"), nullable=False, server_default="queued"),
        sa.Column("hyperparameters", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("gpu_node_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("gpu_nodes.id"), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_runs_experiment_id", "runs", ["experiment_id"])
    op.create_index("ix_runs_status", "runs", ["status"])

    op.create_foreign_key("fk_gpu_nodes_current_run", "gpu_nodes", "runs", ["current_run_id"], ["id"])

    op.create_table(
        "metrics",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("run_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("runs.id"), nullable=False),
        sa.Column("key", sa.String(255), nullable=False),
        sa.Column("value", sa.Float, nullable=False),
        sa.Column("step", sa.Integer, nullable=False),
        sa.Column("epoch", sa.Integer, nullable=True),
        sa.Column("logged_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_metrics_run_key_step", "metrics", ["run_id", "key", "step"])

    op.create_table(
        "artifacts",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("run_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("runs.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("artifact_type", sa.Enum("model", "dataset", "checkpoint", "log", name="artifact_type"), nullable=False),
        sa.Column("uri", sa.String(2048), nullable=False),
        sa.Column("size_bytes", sa.BigInteger, nullable=True),
        sa.Column("checksum", sa.String(128), nullable=True),
        sa.Column("parent_artifact_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("artifacts.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_artifacts_run_id", "artifacts", ["run_id"])

    op.execute("""
        CREATE VIEW experiment_summary AS
        SELECT
            e.id,
            e.name,
            e.tags,
            COUNT(r.id) AS total_runs,
            COUNT(r.id) FILTER (WHERE r.status = 'completed') AS completed_runs,
            COUNT(r.id) FILTER (WHERE r.status = 'failed') AS failed_runs,
            MIN(r.started_at) AS first_run_at,
            MAX(r.finished_at) AS last_run_at
        FROM experiments e
        LEFT JOIN runs r ON r.experiment_id = e.id
        GROUP BY e.id, e.name, e.tags
    """)

    op.execute("""
        CREATE VIEW run_metric_summary AS
        SELECT
            r.id AS run_id,
            r.name AS run_name,
            r.status,
            r.hyperparameters,
            m.key AS metric_key,
            MIN(m.value) AS min_value,
            MAX(m.value) AS max_value,
            AVG(m.value) AS avg_value,
            COUNT(m.id) AS total_steps
        FROM runs r
        JOIN metrics m ON m.run_id = r.id
        GROUP BY r.id, r.name, r.status, r.hyperparameters, m.key
    """)


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS run_metric_summary")
    op.execute("DROP VIEW IF EXISTS experiment_summary")
    op.drop_table("artifacts")
    op.drop_table("metrics")
    op.execute("ALTER TABLE gpu_nodes DROP CONSTRAINT IF EXISTS fk_gpu_nodes_current_run")
    op.drop_table("runs")
    op.drop_table("gpu_nodes")
    op.drop_table("experiments")
    op.execute("DROP TYPE IF EXISTS run_status")
    op.execute("DROP TYPE IF EXISTS artifact_type")
    op.execute("DROP TYPE IF EXISTS gpu_node_status")
