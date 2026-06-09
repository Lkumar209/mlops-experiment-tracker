from datetime import datetime, timezone

from flask import Blueprint, jsonify

from ..extensions import db
from ..middleware.auth import require_api_key
from ..models.gpu_node import GPUNode

gpu_nodes_bp = Blueprint("gpu_nodes", __name__)


@gpu_nodes_bp.route("/gpu-nodes", methods=["GET"])
@require_api_key
def list_gpu_nodes():
    nodes = db.session.query(GPUNode).order_by(GPUNode.name).all()
    return jsonify({"data": [n.to_dict() for n in nodes], "meta": {"total": len(nodes)}})


@gpu_nodes_bp.route("/gpu-nodes/available", methods=["GET"])
@require_api_key
def list_available_gpu_nodes():
    nodes = db.session.query(GPUNode).filter_by(status="available").order_by(GPUNode.memory_gb.desc()).all()
    return jsonify({"data": [n.to_dict() for n in nodes], "meta": {"total": len(nodes)}})


@gpu_nodes_bp.route("/gpu-nodes/<node_id>/heartbeat", methods=["POST"])
@require_api_key
def node_heartbeat(node_id: str):
    node = db.session.query(GPUNode).filter_by(id=node_id).first()
    if not node:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "GPU node not found"}}), 404

    node.last_heartbeat = datetime.now(timezone.utc)
    if node.status == "offline":
        node.status = "available"
    db.session.commit()

    return jsonify({"data": node.to_dict()})
