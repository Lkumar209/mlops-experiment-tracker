import uuid
from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db


class Artifact(db.Model):
    __tablename__ = "artifacts"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("runs.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    artifact_type: Mapped[str] = mapped_column(
        Enum("model", "dataset", "checkpoint", "log", name="artifact_type"),
        nullable=False,
    )
    uri: Mapped[str] = mapped_column(String(2048), nullable=False)
    size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    checksum: Mapped[str | None] = mapped_column(String(128), nullable=True)
    parent_artifact_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("artifacts.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    run: Mapped["Run"] = relationship("Run", back_populates="artifacts")  # type: ignore[name-defined]
    parent: Mapped["Artifact | None"] = relationship("Artifact", remote_side="Artifact.id", back_populates="children")
    children: Mapped[list["Artifact"]] = relationship("Artifact", back_populates="parent")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "run_id": self.run_id,
            "name": self.name,
            "artifact_type": self.artifact_type,
            "uri": self.uri,
            "size_bytes": self.size_bytes,
            "checksum": self.checksum,
            "parent_artifact_id": self.parent_artifact_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
