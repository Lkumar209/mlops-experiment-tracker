import time

import structlog

from ..extensions import db, redis_client
from ..models.gpu_node import GPUNode
from ..models.run import Run

log = structlog.get_logger()

GPU_QUEUE_KEY = "gpu:queue"


class GPUScheduler:
    @staticmethod
    def schedule_run(run_id: str) -> str | None:
        node = (
            db.session.query(GPUNode)
            .filter_by(status="available")
            .order_by(GPUNode.memory_gb.desc())
            .with_for_update(skip_locked=True)
            .first()
        )

        if node:
            node.status = "busy"
            node.current_run_id = run_id
            db.session.flush()
            log.info("run_scheduled_to_node", run_id=run_id, node_id=node.id, node_name=node.name)
            return node.id

        if redis_client:
            redis_client.zadd(GPU_QUEUE_KEY, {run_id: time.time()})
            log.info("run_queued_no_gpu", run_id=run_id)

        return None

    @staticmethod
    def release_node(node_id: str) -> None:
        node = db.session.query(GPUNode).filter_by(id=node_id).with_for_update().first()
        if not node:
            return

        if redis_client:
            next_run = redis_client.zrange(GPU_QUEUE_KEY, 0, 0)
            if next_run:
                next_run_id = next_run[0]
                redis_client.zrem(GPU_QUEUE_KEY, next_run_id)

                run = db.session.query(Run).filter_by(id=next_run_id).first()
                if run:
                    node.current_run_id = next_run_id
                    run.gpu_node_id = node_id
                    run.status = "running"
                    db.session.flush()
                    log.info("queued_run_assigned_to_node", run_id=next_run_id, node_id=node_id)
                    db.session.commit()
                    return

        node.status = "available"
        node.current_run_id = None
        db.session.commit()
        log.info("gpu_node_released", node_id=node_id)
