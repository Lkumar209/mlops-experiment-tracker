from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from ..middleware.auth import require_api_key
from ..models.run import Run
from ..schemas.artifact import ArtifactCreateSchema
from ..services.artifact_service import ArtifactService

artifacts_bp = Blueprint("artifacts", __name__)

_create_schema = ArtifactCreateSchema()


def _get_run_or_404(run_id: str):
    from ..extensions import db

    return db.session.query(Run).filter_by(id=run_id).first()


@artifacts_bp.route("/runs/<run_id>/artifacts", methods=["POST"])
@require_api_key
def create_artifact(run_id: str):
    run = _get_run_or_404(run_id)
    if not run:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Run not found"}}), 404

    try:
        data = _create_schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": e.messages}}), 422

    artifact = ArtifactService.create_artifact(run_id, data)
    return jsonify({"data": artifact.to_dict()}), 201


@artifacts_bp.route("/runs/<run_id>/artifacts", methods=["GET"])
@require_api_key
def list_artifacts(run_id: str):
    run = _get_run_or_404(run_id)
    if not run:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Run not found"}}), 404

    artifacts = ArtifactService.list_artifacts(run_id)
    return jsonify({"data": artifacts, "meta": {"total": len(artifacts)}})


@artifacts_bp.route("/artifacts/<artifact_id>", methods=["GET"])
@require_api_key
def get_artifact(artifact_id: str):
    artifact = ArtifactService.get_artifact(artifact_id)
    if not artifact:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Artifact not found"}}), 404

    return jsonify({"data": artifact.to_dict()})


@artifacts_bp.route("/artifacts/<artifact_id>/lineage", methods=["GET"])
@require_api_key
def get_lineage(artifact_id: str):
    artifact = ArtifactService.get_artifact(artifact_id)
    if not artifact:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Artifact not found"}}), 404

    lineage = ArtifactService.get_lineage(artifact_id)
    return jsonify({"data": lineage})
