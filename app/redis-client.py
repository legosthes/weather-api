import redis
from app.config import REDIS_HOST


def get_redis_client():
    return redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
