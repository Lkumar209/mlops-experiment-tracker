from functools import wraps

import structlog
from flask import current_app, jsonify, request

log = structlog.get_logger()


def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("X-API-Key")
        if not key or key != current_app.config["API_KEY"]:
            log.warning("unauthorized_request", path=request.path, ip=request.remote_addr)
            return jsonify({"error": {"code": "UNAUTHORIZED", "message": "Invalid or missing API key"}}), 401
        return f(*args, **kwargs)

    return decorated
