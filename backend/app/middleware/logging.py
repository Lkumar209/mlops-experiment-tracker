import time

import structlog
from flask import Flask, g, request

log = structlog.get_logger()


def configure_structlog() -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(0),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )


def register_logging(app: Flask) -> None:
    configure_structlog()

    @app.before_request
    def start_timer():
        g.start_time = time.monotonic()

    @app.after_request
    def log_request(response):
        duration_ms = (time.monotonic() - g.get("start_time", time.monotonic())) * 1000
        log.info(
            "http_request",
            method=request.method,
            path=request.path,
            status=response.status_code,
            duration_ms=round(duration_ms, 2),
            ip=request.remote_addr,
        )
        return response
