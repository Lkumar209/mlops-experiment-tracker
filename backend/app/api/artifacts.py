from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
import hashlib
import io
import os
import uuid

from flask import redirect, send_file
from werkzeug.utils import secure_filename

from ..config import settings


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

@artifacts_bp.route("/runs/<run_id>/artifacts/upload", methods=["POST"])
@require_api_key
def upload_artifact(run_id: str):
    run = _get_run_or_404(run_id)
    if not run:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Run not found"}}), 404

    if "file" not in request.files:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "No file in request"}}), 422

    artifact_type = request.form.get("artifact_type", "log")
    if artifact_type not in ("model", "dataset", "checkpoint", "log"):
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "Invalid artifact_type"}}), 422

    file = request.files["file"]
    filename = secure_filename(file.filename or "upload")
    file_bytes = file.read()
    checksum = hashlib.sha256(file_bytes).hexdigest()
    artifact_id = str(uuid.uuid4())

    if settings.s3_bucket:
        uri = _upload_s3(file_bytes, run_id, artifact_id, filename)
    else:
        uri = _save_local(file_bytes, run_id, artifact_id, filename)

    from ..extensions import db
    from ..models.artifact import Artifact as ArtifactModel
    artifact = ArtifactModel(
        id=artifact_id,
        run_id=run_id,
        name=filename,
        artifact_type=artifact_type,
        uri=uri,
        size_bytes=len(file_bytes),
        checksum=checksum,
    )
    db.session.add(artifact)
    db.session.commit()
    return jsonify({"data": artifact.to_dict()}), 201


@artifacts_bp.route("/artifacts/<artifact_id>/download", methods=["GET"])
@require_api_key
def download_artifact(artifact_id: str):
    artifact = ArtifactService.get_artifact(artifact_id)
    if not artifact:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Artifact not found"}}), 404

    uri = artifact.uri

    if uri.startswith("s3://"):
        import boto3
        _, rest = uri[5:].split("/", 1)
        bucket = uri[5:].split("/")[0]
        key = "/".join(uri[5:].split("/")[1:])
        s3 = boto3.client("s3", region_name=settings.s3_region,
                          aws_access_key_id=settings.aws_access_key_id,
                          aws_secret_access_key=settings.aws_secret_access_key)
        url = s3.generate_presigned_url("get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=3600)
        return redirect(url)

    if uri.startswith("local://"):
        path = uri[len("local://"):]
        if not os.path.exists(path):
            return jsonify({"error": {"code": "NOT_FOUND", "message": "File not on disk"}}), 404
        return send_file(path, as_attachment=True, download_name=artifact.name)

    return redirect(uri)


def _save_local(file_bytes: bytes, run_id: str, artifact_id: str, filename: str) -> str:
    dest = os.path.join(settings.artifact_store_path, run_id, artifact_id)
    os.makedirs(dest, exist_ok=True)
    path = os.path.join(dest, filename)
    with open(path, "wb") as f:
        f.write(file_bytes)
    return f"local://{path}"


def _upload_s3(file_bytes: bytes, run_id: str, artifact_id: str, filename: str) -> str:
    import boto3
    key = f"{run_id}/{artifact_id}/{filename}"
    boto3.client("s3", region_name=settings.s3_region,
                 aws_access_key_id=settings.aws_access_key_id,
                 aws_secret_access_key=settings.aws_secret_access_key
                 ).upload_fileobj(io.BytesIO(file_bytes), settings.s3_bucket, key)
    return f"s3://{settings.s3_bucket}/{key}"
