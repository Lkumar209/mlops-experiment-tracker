from flask import Flask
from flask_cors import CORS

from .config import settings
from .extensions import db, migrate, init_redis


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = settings.database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = settings.secret_key
    app.config["REDIS_URL"] = settings.redis_url
    app.config["API_KEY"] = settings.api_key

    if test_config:
        app.config.update(test_config)

    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    init_redis(app)

    from .api.experiments import experiments_bp
    from .api.runs import runs_bp
    from .api.metrics import metrics_bp
    from .api.artifacts import artifacts_bp
    from .api.gpu_nodes import gpu_nodes_bp
    from .api.health import health_bp
    from .api.tags import tags_bp
    from .api.alerts import alerts_bp

    app.register_blueprint(experiments_bp, url_prefix="/api/v1")
    app.register_blueprint(runs_bp, url_prefix="/api/v1")
    app.register_blueprint(metrics_bp, url_prefix="/api/v1")
    app.register_blueprint(artifacts_bp, url_prefix="/api/v1")
    app.register_blueprint(gpu_nodes_bp, url_prefix="/api/v1")
    app.register_blueprint(health_bp)
    app.register_blueprint(tags_bp, url_prefix="/api/v1")
    app.register_blueprint(alerts_bp, url_prefix="/api/v1")

    return app
