import os
import redis
from typing import Optional

class Redis:
    def __init__(self):
        self.host = os.getenv("REDIS_HOST", "localhost")
        self.port = int(os.getenv("REDIS_PORT", 6379))
        self.r = redis.Redis(host=self.host, port=self.port, decode_responses=False)
    
    def has(self, key: str):
        return self.r.exists(key)

    def set(self, key: str, val: str):
        self.r.set(name=key, value=val)
    
    def get(self, key: str, decode: bool = True) -> Optional[str]:
        b = self.r.get(name=key)
        return b if not decode else (b.decode('utf-8') if b is not None else None)
    
    def delete(self, key: str):
        self.r.delete(key)
    
    def delete_all(self, pattern: str):
        for key in self.r.scan_iter(pattern):
            self.r.delete(key)