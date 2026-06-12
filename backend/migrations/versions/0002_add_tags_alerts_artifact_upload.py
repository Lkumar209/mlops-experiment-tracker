"""add run_tags and alert_configs tables

Revision ID: 0002_add_tags_alerts_artifact_upload
Revises: 0001_initial_schema
Create Date: 2026-06-12 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_add_tags_alerts_artifact_upload"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "run_tags",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("run_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("runs.id"), nullable=False),
        sa.Column("key", sa.String(255), nullable=False),
        sa.Column("value", sa.String(1024), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("run_id", "key", name="uq_run_tags_run_key"),
    )
    op.create_index("ix_run_tags_run_id", "run_tags", ["run_id"])
    op.create_index("ix_run_tags_key", "run_tags", ["key"])

    op.execute("CREATE TYPE alert_condition AS ENUM ('lt', 'gt', 'lte', 'gte')")
    op.create_table(
        "alert_configs",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("experiment_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("experiments.id"), nullable=False),
        sa.Column("metric_key", sa.String(255), nullable=False),
        sa.Column("condition", sa.Enum("lt", "gt", "lte", "gte", name="alert_condition"), nullable=False),
        sa.Column("threshold", sa.Float, nullable=False),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_alert_configs_experiment_id", "alert_configs", ["experiment_id"])


def downgrade() -> None:
    op.drop_table("alert_configs")
    op.execute("DROP TYPE IF EXISTS alert_condition")
    op.drop_table("run_tags")
