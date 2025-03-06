import uuid
import docker as dk
import os
from typing import Optional, Type, TypeVar
from enum import Enum
from .redis import Redis
from .query import Query, QueryStatus

def get_docker() -> dk.DockerClient:
    return dk.from_env()

def get_container(name: str):
    try:
        docker = get_docker()
        return docker.containers.get(name)
    except dk.errors.NotFound:
        return None

class AnalyzerStatus(Enum):
    REQUESTED = "REQUESTED"
    SPAWNED = "SPAWNED"
    CLONING = "CLONING"
    PROCESSING = "PROCESSING"
    READY = "READY"
    ERROR = "ERROR"

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
    
    def exists(self) -> bool:
        return self.redis.has(self._status_key)

    def set_status(self, status: AnalyzerStatus):
        self.redis.set(self._status_key, status.value)
    
    def get_status(self) -> Optional[AnalyzerStatus]:
        status = self.redis.get(self._status_key)
        return AnalyzerStatus(status) if status else None
    
    def spawn_container(self):
        assert self.github_url

        docker = get_docker()
        network = docker.networks.get("llm_net")
        container = docker.containers.run(
            "analyzer_worker",
            name=self._worker_name,
            detach=True,
            auto_remove=True,
            network="redis_net",
            environment=[
                f"REQUEST_ID={self.id}",
                f"GITHUB_URL={self.github_url}",
                f"REDIS_HOST={self.redis.host}",
                f"REDIS_PORT={self.redis.port}",
                f"LLM_API_KEY={os.environ.get('LLM_API_KEY', 'API_KEY')}"
            ]
        )
        network.connect(container)
    
    def push_query(self, query: Query):
        query.set_status(QueryStatus.REQUESTED)
        self.redis.push(self._queue_name, query.to_json())
        self.redis.push(self._query_list_name, query.id)
    
    def pull_query(self) -> Optional[Query]:
        s = self.redis.pull(self._queue_name)
        if s is not None:
            return Query.from_json(s)
        else:
            return None

    def delete(self):
        container = get_container(self._worker_name)
        if container:
            container.remove(force=True)
        self.delete_records()
    
    def delete_records(self):
        for qid in self._query_ids:
            self.redis.delete_all(f"{Query.from_id(qid)._redis_prefix}*")
        self.redis.delete_all(f"{self._redis_prefix}*")
    
    @property
    def _query_ids(self) -> list[str]:
        return self.redis.range(self._query_list_name, 0, -1)
    @property
    def _worker_name(self) -> str:
        return f"worker-{self.id}"
    @property
    def _redis_prefix(self) -> str:
        return f"analyzer:{self.id}"
    @property
    def _status_key(self) -> str:
        return f"{self._redis_prefix}:status"
    @property
    def _queue_name(self) -> str:
        return f"{self._redis_prefix}:queue"
    @property
    def _query_list_name(self) -> str:
        return f"{self._redis_prefix}:querylist"
