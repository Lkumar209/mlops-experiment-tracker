from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from ..middleware.auth import require_api_key
from ..models.experiment import Experiment
from ..schemas.run import RunCreateSchema, RunStatusUpdateSchema
from ..services.run_service import RunService

runs_bp = Blueprint("runs", __name__)

_create_schema = RunCreateSchema()
_status_schema = RunStatusUpdateSchema()


@runs_bp.route("/experiments/<experiment_id>/runs", methods=["GET"])
@require_api_key
def list_runs(experiment_id: str):
    from ..extensions import db

    experiment = db.session.query(Experiment).filter_by(id=experiment_id).first()
    if not experiment:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Experiment not found"}}), 404

    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)
    status = request.args.get("status")

    runs, total = RunService.list_runs(experiment_id, page=page, per_page=per_page, status=status)
    return jsonify({"data": runs, "meta": {"page": page, "per_page": per_page, "total": total}})


@runs_bp.route("/experiments/<experiment_id>/runs", methods=["POST"])
@require_api_key
def create_run(experiment_id: str):
    from ..extensions import db

    experiment = db.session.query(Experiment).filter_by(id=experiment_id).first()
    if not experiment:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Experiment not found"}}), 404

    try:
        data = _create_schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": e.messages}}), 422

    run = RunService.create_run(experiment_id=experiment_id, name=data["name"], hyperparameters=data.get("hyperparameters", {}))
    return jsonify({"data": run.to_dict()}), 201


@runs_bp.route("/runs/<run_id>", methods=["GET"])
@require_api_key
def get_run(run_id: str):
    run = RunService.get_run(run_id)
    if not run:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Run not found"}}), 404

    return jsonify({"data": run.to_dict()})


@runs_bp.route("/runs/<run_id>/status", methods=["PATCH"])
@require_api_key
def update_run_status(run_id: str):
    try:
        data = _status_schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": e.messages}}), 422

    run = RunService.update_status(run_id, data["status"])
    if not run:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Run not found"}}), 404

    return jsonify({"data": run.to_dict()})


@runs_bp.route("/runs/<run_id>", methods=["DELETE"])
@require_api_key
def delete_run(run_id: str):
    deleted = RunService.delete_run(run_id)
    if not deleted:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Run not found"}}), 404

    return jsonify({"data": {"deleted": True}})
