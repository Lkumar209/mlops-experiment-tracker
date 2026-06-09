import json

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from ..middleware.auth import require_api_key
from ..schemas.experiment import ExperimentCreateSchema, ExperimentUpdateSchema
from ..services.experiment_service import ExperimentService

experiments_bp = Blueprint("experiments", __name__)

_create_schema = ExperimentCreateSchema()
_update_schema = ExperimentUpdateSchema()


@experiments_bp.route("/experiments", methods=["GET"])
@require_api_key
def list_experiments():
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)
    sort_by = request.args.get("sort_by", "created_at")
    tags_raw = request.args.get("tags")

    tags_filter = None
    if tags_raw:
        try:
            tags_filter = json.loads(tags_raw)
        except (ValueError, TypeError):
            return jsonify({"error": {"code": "INVALID_PARAMS", "message": "tags must be valid JSON"}}), 400

    experiments, total = ExperimentService.list_experiments(page=page, per_page=per_page, tags_filter=tags_filter, sort_by=sort_by)
    return jsonify({"data": experiments, "meta": {"page": page, "per_page": per_page, "total": total}})


@experiments_bp.route("/experiments", methods=["POST"])
@require_api_key
def create_experiment():
    try:
        data = _create_schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": e.messages}}), 422

    try:
        experiment = ExperimentService.create_experiment(
            name=data["name"],
            description=data.get("description"),
            tags=data.get("tags", {}),
        )
    except ValueError as e:
        return jsonify({"error": {"code": "CONFLICT", "message": str(e)}}), 409

    return jsonify({"data": experiment.to_dict()}), 201


@experiments_bp.route("/experiments/<experiment_id>", methods=["GET"])
@require_api_key
def get_experiment(experiment_id: str):
    experiment = ExperimentService.get_experiment(experiment_id)
    if not experiment:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Experiment not found"}}), 404

    data = experiment.to_dict()
    data["runs"] = [r.to_dict() for r in experiment.runs]
    return jsonify({"data": data})


@experiments_bp.route("/experiments/<experiment_id>", methods=["PUT"])
@require_api_key
def update_experiment(experiment_id: str):
    try:
        data = _update_schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": e.messages}}), 422

    try:
        experiment = ExperimentService.update_experiment(experiment_id, data)
    except ValueError as e:
        return jsonify({"error": {"code": "CONFLICT", "message": str(e)}}), 409

    if not experiment:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Experiment not found"}}), 404

    return jsonify({"data": experiment.to_dict()})


@experiments_bp.route("/experiments/<experiment_id>", methods=["DELETE"])
@require_api_key
def delete_experiment(experiment_id: str):
    deleted = ExperimentService.delete_experiment(experiment_id)
    if not deleted:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Experiment not found"}}), 404

    return jsonify({"data": {"deleted": True}})
