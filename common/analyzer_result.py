import json
from typing import Optional, Dict, Type, TypeVar

T = TypeVar('T', bound='AnalyzerResult')

class AnalyzerResult:
    @classmethod
    def from_json(cls: Type[T], json_str: str) -> T:
        d = json.loads(json_str)
        return AnalyzerResult(
            paths=d["paths"],
            tree=d["tree"],
        )

    def __init__(self, paths, tree):
        self.paths = paths
        self.tree = tree
    
    def to_dict(self) -> Dict:
        return {
            "paths": self.paths,
            "tree": self.tree
        }
    
    def to_json(self, indent: Optional[int] = None) -> str:
        return json.dumps(self.to_dict(), indent=indent)