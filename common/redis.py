import os
from redis import Redis

def get_redis(host: str = None, port: int = None):
    host = host if host is not None else os.getenv("REDIS_HOST", "localhost")
    port = port if port is not None else int(os.getenv("REDIS_PORT", 6379))
    return Redis(host=host, port=port, decode_responses=True)
