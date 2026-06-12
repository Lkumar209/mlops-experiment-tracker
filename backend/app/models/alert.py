import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db


class AlertConfig(db.Model):
    __tablename__ = "alert_configs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    experiment_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("experiments.id"), nullable=False)
    metric_key: Mapped[str] = mapped_column(String(255), nullable=False)
    condition: Mapped[str] = mapped_column(
        Enum("lt", "gt", "lte", "gte", name="alert_condition"), nullable=False
    )
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    experiment: Mapped["Experiment"] = relationship("Experiment")  # type: ignore[name-defined]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "experiment_id": self.experiment_id,
            "metric_key": self.metric_key,
            "condition": self.condition,
            "threshold": self.threshold,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def check(self, value: float) -> bool:
        ops = {"lt": value < self.threshold, "gt": value > self.threshold,
               "lte": value <= self.threshold, "gte": value >= self.threshold}
        return ops.get(self.condition, False)
