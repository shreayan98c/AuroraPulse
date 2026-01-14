from loguru import logger
from rq import Queue
from src.backend.redis_handler.redis_conn import redis_conn
from src.backend.redis_handler.rq_tasks import check_aurora_alerts

q = Queue("aurora", connection=redis_conn)
q.enqueue(check_aurora_alerts)

logger.info("Enqueued check_aurora_alerts task.")
