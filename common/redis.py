import os
import redis
from typing import Optional

class Redis:
    def __init__(self):
        self.host = os.getenv("REDIS_HOST", "localhost")
        self.port = int(os.getenv("REDIS_PORT", 6379))
        self.r = redis.Redis(host=self.host, port=self.port, decode_responses=True)
    
    def set(self, key: str, val: str):
        self.r.set(name=key, value=val)
    
    def get(self, key: str) -> Optional[str]:
        return self.r.get(name=key)