import json
from typing import Optional, Dict, Type, TypeVar

T = TypeVar('T', bound='AnalyzerResult')

class AnalyzerResult:
    @classmethod
    def from_json(cls: Type[T], json_str: str) -> T:
        d = json.loads(json_str)
        return AnalyzerResult(
            repo_metadata=d["repo_metadata"]
        )

    def __init__(self, repo_metadata: str):
        self.repo_metadata = repo_metadata
    
    def to_dict(self) -> Dict:
        return {
            "repo_metadata": self.repo_metadata
        }
    
    def to_json(self, indent: Optional[int] = None) -> str:
        return json.dumps(self.to_dict(), indent=indent)