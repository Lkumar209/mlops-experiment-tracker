import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db


class RunTag(db.Model):
    __tablename__ = "run_tags"
    __table_args__ = (UniqueConstraint("run_id", "key", name="uq_run_tags_run_key"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("runs.id"), nullable=False)
    key: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[str] = mapped_column(String(1024), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    run: Mapped["Run"] = relationship("Run", back_populates="tags")  # type: ignore[name-defined]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "run_id": self.run_id,
            "key": self.key,
            "value": self.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
