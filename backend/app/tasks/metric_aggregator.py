import json
import threading

import structlog

from ..extensions import redis_client

log = structlog.get_logger()

_aggregator_thread: threading.Thread | None = None


def _run_aggregator() -> None:
    if not redis_client:
        log.warning("metric_aggregator_skipped", reason="no redis client")
        return

    pubsub = redis_client.pubsub()
    pubsub.psubscribe("run:*:metrics")
    log.info("metric_aggregator_started")

    try:
        for message in pubsub.listen():
            if message["type"] != "pmessage":
                continue

            try:
                data = json.loads(message["data"])
                run_id = data.get("run_id")
                key = data.get("key")
                value = data.get("value")

                if run_id and key is not None and value is not None:
                    redis_client.hset(f"run:{run_id}:latest_metrics", key, json.dumps({"value": value, "step": data.get("step")}))
            except (json.JSONDecodeError, KeyError) as e:
                log.error("metric_aggregator_parse_error", error=str(e))
    except Exception as e:
        log.error("metric_aggregator_error", error=str(e))
    finally:
        pubsub.unsubscribe()
        pubsub.close()


def start_aggregator() -> None:
    global _aggregator_thread
    if _aggregator_thread and _aggregator_thread.is_alive():
        return

    _aggregator_thread = threading.Thread(target=_run_aggregator, daemon=True, name="metric-aggregator")
    _aggregator_thread.start()
    log.info("metric_aggregator_thread_started")
