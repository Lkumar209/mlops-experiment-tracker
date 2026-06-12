from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from ..middleware.auth import require_api_key
from ..models.experiment import Experiment
from ..schemas.run import RunCreateSchema, RunStatusUpdateSchema
from ..services.run_service import RunService

runs_bp = Blueprint("runs", __name__)

_create_schema = RunCreateSchema()
_status_schema = RunStatusUpdateSchema()

@runs_bp.route("/runs/compare", methods=["GET"])
@require_api_key
def compare_runs():
    from ..extensions import db
    from ..models.metric import Metric

    ids_param = request.args.get("ids", "")
    run_ids = [i.strip() for i in ids_param.split(",") if i.strip()]
    if not run_ids:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "ids query param required"}}), 422
    if len(run_ids) > 10:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "Cannot compare more than 10 runs"}}), 422

    from ..models.run import Run
    runs = db.session.query(Run).filter(Run.id.in_(run_ids)).all()
    found_ids = {r.id for r in runs}
    missing = [i for i in run_ids if i not in found_ids]
    if missing:
        return jsonify({"error": {"code": "NOT_FOUND", "message": f"Runs not found: {missing}"}}), 404

    metrics = (
        db.session.query(Metric)
        .filter(Metric.run_id.in_(run_ids))
        .order_by(Metric.run_id, Metric.key, Metric.step)
        .all()
    )

    runs_data = {r.id: {"run": r.to_dict(), "metrics": {}} for r in runs}
    for m in metrics:
        if m.key not in runs_data[m.run_id]["metrics"]:
            runs_data[m.run_id]["metrics"][m.key] = []
        runs_data[m.run_id]["metrics"][m.key].append(
            {"step": m.step, "value": m.value, "epoch": m.epoch}
        )

    all_keys = sorted({k for r in runs_data.values() for k in r["metrics"]})
    return jsonify({"data": {"runs": runs_data, "metric_keys": all_keys}})


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
