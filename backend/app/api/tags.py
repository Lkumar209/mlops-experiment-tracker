from flask import Blueprint, jsonify, request
from marshmallow import Schema, ValidationError, fields

from ..extensions import db
from ..middleware.auth import require_api_key
from ..models.run import Run
from ..models.tag import RunTag

tags_bp = Blueprint("tags", __name__)


class TagSchema(Schema):
    key = fields.Str(required=True)
    value = fields.Str(required=True)


_schema = TagSchema()


@tags_bp.route("/runs/<run_id>/tags", methods=["GET"])
@require_api_key
def list_tags(run_id: str):
    if not db.session.query(Run).filter_by(id=run_id).first():
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Run not found"}}), 404
    tags = db.session.query(RunTag).filter_by(run_id=run_id).all()
    return jsonify({"data": [t.to_dict() for t in tags]})


@tags_bp.route("/runs/<run_id>/tags", methods=["POST"])
@require_api_key
def set_tag(run_id: str):
    if not db.session.query(Run).filter_by(id=run_id).first():
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Run not found"}}), 404
    try:
        data = _schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": e.messages}}), 422

    existing = db.session.query(RunTag).filter_by(run_id=run_id, key=data["key"]).first()
    if existing:
        existing.value = data["value"]
        db.session.commit()
        return jsonify({"data": existing.to_dict()})

    tag = RunTag(run_id=run_id, key=data["key"], value=data["value"])
    db.session.add(tag)
    db.session.commit()
    return jsonify({"data": tag.to_dict()}), 201


@tags_bp.route("/runs/<run_id>/tags/<key>", methods=["DELETE"])
@require_api_key
def delete_tag(run_id: str, key: str):
    tag = db.session.query(RunTag).filter_by(run_id=run_id, key=key).first()
    if not tag:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Tag not found"}}), 404
    db.session.delete(tag)
    db.session.commit()
    return jsonify({"data": {"deleted": True}})
