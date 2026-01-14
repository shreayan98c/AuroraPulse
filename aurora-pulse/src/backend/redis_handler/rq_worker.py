from loguru import logger
from rq import Queue, SimpleWorker, Worker

from .redis_conn import redis_conn

if __name__ == "__main__":
    logger.info("Starting RQ Worker...")
    q = Queue("aurora", connection=redis_conn)
    # worker = Worker([q])  # does not work on Windows
    worker = SimpleWorker([q], connection=redis_conn)
    worker.work()
