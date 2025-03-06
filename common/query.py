import uuid
import docker as dk
import os
from typing import Optional, Type, TypeVar, Dict
from enum import Enum
import json
from .redis import Redis

class QueryStatus(Enum):
    REQUESTED = "REQUESTED"
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    ERROR = "ERROR"

Q = TypeVar('Q', bound='QueryResult')
class QueryResult:
    @classmethod
    def from_json(cls: Type[Q], json_str: str) -> Q:
        d = json.loads(json_str)
        return QueryResult(
            query = d["query"],
            result = d["result"]
        )

    def __init__(self, query: str, result: str):
        self.query = query
        self.result = result
    
    def to_dict(self) -> Dict:
        return {
            "query": self.query,
            "result": self.result
        }
    
    def to_json(self, indent: Optional[int] = None) -> str:
        return json.dumps(self.to_dict(), indent=indent)
    
T = TypeVar('T', bound='Query')
class Query:
    @classmethod
    def from_json(cls: Type[T], s: str) -> T:
        d = json.loads(s)
        return Query(d["id"], d["query"])
    
    @classmethod
    def from_query(cls: Type[T], q: str) -> T:
        return Query(str(uuid.uuid4().hex), q)
    
    @classmethod
    def from_id(cls: Type[T], id: str) -> T:
        return Query(id, "")

    def __init__(self, id: str, query: str):
        self.id = id
        self.query = query
        self.redis = Redis()

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "query": self.query
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())
    
    def exists(self) -> bool:
        return self.redis.has(self._status_key)
    
    def set_status(self, status: QueryStatus):
        self.redis.set(self._status_key, status.value)
    
    def get_status(self) -> Optional[QueryStatus]:
        status = self.redis.get(self._status_key)
        return QueryStatus(status) if status else None
    
    def set_result(self, result: QueryResult):
        self.redis.set(self._result_key, result.to_json())
        self.set_status(QueryStatus.DONE)
    
    def get_result(self) -> Optional[QueryResult]:
        result = self.redis.get(self._result_key)
        return QueryResult.from_json(result) if result else None
    
    @property
    def _redis_prefix(self) -> str:
        return f"query:{self.id}"
    @property
    def _status_key(self) -> str:
        return f"{self._redis_prefix}:status"
    @property
    def _result_key(self) -> str:
        return f"{self._redis_prefix}:result"