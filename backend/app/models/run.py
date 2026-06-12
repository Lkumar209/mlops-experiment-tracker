import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db

RunStatus = Enum("queued", "running", "completed", "failed", name="run_status")


class Run(db.Model):
    __tablename__ = "runs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    experiment_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("experiments.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("queued", "running", "completed", "failed", name="run_status"),
        nullable=False,
        default="queued",
    )
    hyperparameters: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    gpu_node_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("gpu_nodes.id"), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    experiment: Mapped["Experiment"] = relationship("Experiment", back_populates="runs")  # type: ignore[name-defined]
    metrics: Mapped[list["Metric"]] = relationship("Metric", back_populates="run", cascade="all, delete-orphan")  # type: ignore[name-defined]
    artifacts: Mapped[list["Artifact"]] = relationship("Artifact", back_populates="run", cascade="all, delete-orphan")  # type: ignore[name-defined]
    tags: Mapped[list["RunTag"]] = relationship("RunTag", back_populates="run", cascade="all, delete-orphan")  # type: ignore[name-defined]
    gpu_node: Mapped["GPUNode | None"] = relationship("GPUNode", foreign_keys=[gpu_node_id])  # type: ignore[name-defined]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "experiment_id": self.experiment_id,
            "name": self.name,
            "status": self.status,
            "hyperparameters": self.hyperparameters,
            "gpu_node_id": self.gpu_node_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
