import structlog

from ..extensions import db
from ..models.artifact import Artifact

log = structlog.get_logger()


class ArtifactService:
    @staticmethod
    def create_artifact(run_id: str, data: dict) -> Artifact:
        artifact = Artifact(
            run_id=run_id,
            name=data["name"],
            artifact_type=data["artifact_type"],
            uri=data["uri"],
            size_bytes=data.get("size_bytes"),
            checksum=data.get("checksum"),
            parent_artifact_id=data.get("parent_artifact_id"),
        )
        db.session.add(artifact)
        db.session.commit()
        log.info("artifact_created", artifact_id=artifact.id, run_id=run_id)
        return artifact

    @staticmethod
    def list_artifacts(run_id: str) -> list[dict]:
        artifacts = db.session.query(Artifact).filter_by(run_id=run_id).order_by(Artifact.created_at.asc()).all()
        return [a.to_dict() for a in artifacts]

    @staticmethod
    def get_artifact(artifact_id: str) -> Artifact | None:
        return db.session.query(Artifact).filter_by(id=artifact_id).first()

    @staticmethod
    def get_lineage(artifact_id: str) -> list[dict]:
        chain = []
        current_id = artifact_id
        visited = set()

        while current_id and current_id not in visited:
            visited.add(current_id)
            artifact = db.session.query(Artifact).filter_by(id=current_id).first()
            if not artifact:
                break
            chain.insert(0, artifact.to_dict())
            current_id = artifact.parent_artifact_id

        children = db.session.query(Artifact).filter_by(parent_artifact_id=artifact_id).all()
        chain.append({"children": [c.to_dict() for c in children]})
        return chain
