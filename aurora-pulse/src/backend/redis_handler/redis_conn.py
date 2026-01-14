import os

import redis
from loguru import logger

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

redis_conn = redis.from_url(REDIS_URL)
logger.info(f"Connected to Redis at {REDIS_URL}")
