from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import redis as redis_lib

db = SQLAlchemy()
migrate = Migrate()
redis_client: redis_lib.Redis | None = None


def init_redis(app) -> None:
    global redis_client
    redis_client = redis_lib.from_url(app.config["REDIS_URL"], decode_responses=True)
