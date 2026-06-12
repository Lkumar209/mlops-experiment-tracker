from flask import Blueprint, jsonify, request
from marshmallow import Schema, ValidationError, fields, validate

from ..extensions import db
from ..middleware.auth import require_api_key
from ..models.alert import AlertConfig
from ..models.experiment import Experiment

alerts_bp = Blueprint("alerts", __name__)


class AlertConfigSchema(Schema):
    metric_key = fields.Str(required=True)
    condition = fields.Str(required=True, validate=validate.OneOf(["lt", "gt", "lte", "gte"]))
    threshold = fields.Float(required=True)
    enabled = fields.Bool(load_default=True)


_schema = AlertConfigSchema()


@alerts_bp.route("/experiments/<experiment_id>/alerts", methods=["GET"])
@require_api_key
def list_alerts(experiment_id: str):
    if not db.session.query(Experiment).filter_by(id=experiment_id).first():
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Experiment not found"}}), 404
    alerts = db.session.query(AlertConfig).filter_by(experiment_id=experiment_id).all()
    return jsonify({"data": [a.to_dict() for a in alerts]})


@alerts_bp.route("/experiments/<experiment_id>/alerts", methods=["POST"])
@require_api_key
def create_alert(experiment_id: str):
    if not db.session.query(Experiment).filter_by(id=experiment_id).first():
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Experiment not found"}}), 404
    try:
        data = _schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": e.messages}}), 422

    alert = AlertConfig(experiment_id=experiment_id, **data)
    db.session.add(alert)
    db.session.commit()
    return jsonify({"data": alert.to_dict()}), 201


@alerts_bp.route("/alerts/<alert_id>", methods=["PATCH"])
@require_api_key
def update_alert(alert_id: str):
    alert = db.session.query(AlertConfig).filter_by(id=alert_id).first()
    if not alert:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Alert not found"}}), 404

    data = request.get_json() or {}
    if "enabled" in data:
        alert.enabled = bool(data["enabled"])
    if "threshold" in data:
        alert.threshold = float(data["threshold"])
    if "condition" in data and data["condition"] in ("lt", "gt", "lte", "gte"):
        alert.condition = data["condition"]

    db.session.commit()
    return jsonify({"data": alert.to_dict()})


@alerts_bp.route("/alerts/<alert_id>", methods=["DELETE"])
@require_api_key
def delete_alert(alert_id: str):
    alert = db.session.query(AlertConfig).filter_by(id=alert_id).first()
    if not alert:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Alert not found"}}), 404
    db.session.delete(alert)
    db.session.commit()
    return jsonify({"data": {"deleted": True}})
