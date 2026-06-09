import json
import time

from flask import Blueprint, Response, jsonify, request, stream_with_context
from marshmallow import ValidationError

from ..extensions import redis_client
from ..middleware.auth import require_api_key
from ..models.run import Run
from ..schemas.metric import MetricBulkIngestSchema
from ..services.metric_service import MetricService

metrics_bp = Blueprint("metrics", __name__)

_bulk_schema = MetricBulkIngestSchema()


def _get_run_or_404(run_id: str):
    from ..extensions import db

    run = db.session.query(Run).filter_by(id=run_id).first()
    return run


@metrics_bp.route("/runs/<run_id>/metrics", methods=["POST"])
@require_api_key
def bulk_ingest_metrics(run_id: str):
    run = _get_run_or_404(run_id)
    if not run:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Run not found"}}), 404

    try:
        data = _bulk_schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": e.messages}}), 422

    count = MetricService.bulk_ingest(run_id, data["metrics"])
    return jsonify({"data": {"ingested": count}}), 201


@metrics_bp.route("/runs/<run_id>/metrics", methods=["GET"])
@require_api_key
def get_metric_keys(run_id: str):
    run = _get_run_or_404(run_id)
    if not run:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Run not found"}}), 404

    keys = MetricService.get_metric_keys(run_id)
    return jsonify({"data": keys})


@metrics_bp.route("/runs/<run_id>/metrics/compare", methods=["GET"])
@require_api_key
def compare_metrics(run_id: str):
    key = request.args.get("key")
    run_ids_raw = request.args.get("run_ids", "")
    run_ids = [r.strip() for r in run_ids_raw.split(",") if r.strip()]
    if run_id not in run_ids:
        run_ids.insert(0, run_id)

    if not key:
        return jsonify({"error": {"code": "INVALID_PARAMS", "message": "key parameter is required"}}), 400

    data = MetricService.get_compare_metrics(run_ids, key)
    return jsonify({"data": data})


@metrics_bp.route("/runs/<run_id>/metrics/<key>", methods=["GET"])
@require_api_key
def get_loss_curve(run_id: str, key: str):
    run = _get_run_or_404(run_id)
    if not run:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Run not found"}}), 404

    curve = MetricService.get_loss_curve(run_id, key)
    return jsonify({"data": curve})


@metrics_bp.route("/runs/<run_id>/metrics/stream", methods=["GET"])
def stream_metrics(run_id: str):
    api_key = request.headers.get("X-API-Key") or request.args.get("api_key")
    from flask import current_app

    if not api_key or api_key != current_app.config["API_KEY"]:
        return jsonify({"error": {"code": "UNAUTHORIZED", "message": "Invalid or missing API key"}}), 401

    def generate():
        if not redis_client:
            yield "data: {}\n\n"
            return

        pubsub = redis_client.pubsub()
        pubsub.subscribe(f"run:{run_id}:metrics")

        try:
            start = time.time()
            while True:
                if time.time() - start > 300:
                    break

                message = pubsub.get_message(timeout=1.0)
                if message and message["type"] == "message":
                    yield f"data: {message['data']}\n\n"
                else:
                    yield ": heartbeat\n\n"
        finally:
            pubsub.unsubscribe()
            pubsub.close()

    return Response(
        stream_with_context(generate()),
        content_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
