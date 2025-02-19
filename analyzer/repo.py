import re
import json
from typing import Optional, List, Dict, Type, TypeVar
from github import Github
from git import Repo
from pathlib import Path

REPO_PATH = "./repo"
IGNORE_DIRS = [".git"]
IGNORE_FILES = [".gitignore"]

T = TypeVar('T', bound='RepoFile')
class RepoFile:
    def __init__(self, path: Path):
        self._path = path
        self._is_file = self._path.is_file()
        self._entries = []
        self._name = self._path.name
        self._type = "dir" if self.is_dir else self._path.suffix
        self._size = self._path.stat().st_size
        if not self.is_file:
            for entry in self._path.iterdir():
                if entry.is_dir() and entry.name not in IGNORE_DIRS:
                    self._entries.append(entry)
                elif entry.is_file() and entry.name not in IGNORE_FILES:
                    self._entries.append(entry)
    
    def to_dict(self) -> Dict:
        entries = list(map(lambda entry: entry.to_dict(), self.entries))
        return {
            "name": self.name,
            "type": self.type,
            "size": self.size,
            "is_dir": self.is_dir,
            "entries": entries
        }
    
    def to_json(self, indent=None) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @property
    def path(self) -> str:
        return str(self._path)
    @property
    def name(self) -> str:
        return self._name
    @property
    def type(self) -> str:
        return self._type
    @property
    def size(self) -> int:
        return self._size
    @property
    def is_dir(self) -> bool:
        return not self._is_file
    @property
    def is_file(self) -> bool:
        return self._is_file
    @property
    def entry_paths(self) -> List[Path]:
        return self._entries 
    @property
    def entries(self) -> List[T]:
        return list(map(lambda path: RepoFile(path), self.entry_paths))
    
class Repository:
    def __init__(self, url: str):
        self.id = Repository.extract_id(url)
        self.repo = Github().get_repo(self.id) if self.id else None
        self.repo_path = Path(REPO_PATH)
        if self.repo_path.exists():
            self.cloned_repo = Repo(REPO_PATH)
        else:
            self.cloned_repo = Repo.clone_from(self.repo.clone_url, REPO_PATH)

    @property
    def root(self) -> RepoFile:
        return RepoFile(self.repo_path)
    
    @property
    def paths(self) -> List[str]:
        paths = []
        def dfs(node: RepoFile):
            paths.append(node.path)
            for entry in node.entries:
                dfs(entry)
        dfs(self.root)
        return paths

    @staticmethod
    def extract_id(url: str) -> Optional[str]:
        match = re.search("(?<=github\.com/)([^/]+/[^/]+)", url) 
        return match.group(0) if match else None
    