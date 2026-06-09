import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db


class GPUNode(db.Model):
    __tablename__ = "gpu_nodes"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    gpu_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    memory_gb: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("available", "busy", "offline", name="gpu_node_status"),
        nullable=False,
        default="available",
    )
    current_run_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("runs.id"), nullable=True)
    last_heartbeat: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    current_run: Mapped["Run | None"] = relationship("Run", foreign_keys=[current_run_id])  # type: ignore[name-defined]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "gpu_count": self.gpu_count,
            "memory_gb": self.memory_gb,
            "status": self.status,
            "current_run_id": self.current_run_id,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
        }
