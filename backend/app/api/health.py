from flask import Blueprint, jsonify

from ..extensions import db, redis_client

health_bp = Blueprint("health", __name__)


def _check_db() -> bool:
    try:
        db.session.execute(db.text("SELECT 1"))
        return True
    except Exception:
        return False


def _check_redis() -> bool:
    try:
        if redis_client:
            redis_client.ping()
            return True
        return False
    except Exception:
        return False


@health_bp.route("/health", methods=["GET"])
def health():
    db_ok = _check_db()
    redis_ok = _check_redis()
    return jsonify({"status": "ok", "db": db_ok, "redis": redis_ok})


@health_bp.route("/readiness", methods=["GET"])
def readiness():
    db_ok = _check_db()
    redis_ok = _check_redis()

    if db_ok and redis_ok:
        return jsonify({"status": "ready"}), 200

    return jsonify({"status": "not_ready", "db": db_ok, "redis": redis_ok}), 503
