import uuid
import docker as dk
import os
from typing import Optional, Type, TypeVar
from enum import Enum
from .redis import Redis

def get_docker() -> dk.DockerClient:
    return dk.from_env()

class AnalyzerStatus(Enum):
    REQUESTED = "REQUESTED"
    SPAWNED = "SPAWNED"
    PROCESSING = "PROCESSING"
    DONE = "DONE"

T = TypeVar('T', bound='Analyzer')

class Analyzer:
    @classmethod
    def new(cls: Type[T], redis: Redis, github_url: str) -> T:
        return Analyzer(
            redis=redis,
            github_url=github_url,
            id=str(uuid.uuid4().hex)
        )
    
    @classmethod
    def from_id(cls: Type[T], redis: Redis, id: str) -> T:
        return Analyzer(
            redis=redis,
            github_url=None,
            id=id
        )
    
    @classmethod
    def from_env(cls: Type[T], redis: Redis) -> T:
        return Analyzer(
            redis=redis,
            github_url=os.getenv("GITHUB_URL"),
            id=os.getenv("REQUEST_ID"),
        )

    def __init__(
        self, 
        redis: Redis,
        github_url: Optional[str] = None,
        id: Optional[str] = None
    ):
        self.redis = redis
        self.github_url = github_url
        self.id = id

    def set_status(self, status: AnalyzerStatus):
        self.redis.set(self._status_key(), status.value)
    
    def get_status(self) -> Optional[AnalyzerStatus]:
        status = self.redis.get(self._status_key())
        return AnalyzerStatus(status) if status else None
    
    def spawn_container(self):
        assert self.github_url

        docker = get_docker()
        docker.containers.run(
            "analyzer_worker",
            name=self._get_worker_name(),
            detach=True,
            auto_remove=True,
            network="redis_net",
            environment=[
                f"REQUEST_ID={self.id}",
                f"GITHUB_URL={self.github_url}",
                f"REDIS_HOST={self.redis.host}",
                f"REDIS_PORT={self.redis.port}"
            ]
        )

    def _get_worker_name(self) -> str:
        return f"worker-{self.id}"
    
    def _redis_prefix(self) -> str:
        return f"analyzer:{self.id}"
    
    def _status_key(self) -> str:
        return f"{self._redis_prefix()}:status"