from repo import Repository
from parsing import parse, DirChunk

class Prompter:
    def __init__(self, repo: Repository):
        self.repo = repo
        self.chunks = parse(self.repo)
        self.repo_metadata = self._build_repo_metadata()

    def _build_repo_metadata(self) -> str:
        dir_metadata = []
        for dir in self.chunks.dirs:
            chunk = self.chunks.load_dir_chunk(dir)
            dir_metadata.append(self._build_dir_metadata(chunk))
        joined_metadata = "".join(dir_metadata)
        return \
f'''Repository: {self.repo.id}
Directories:
{joined_metadata}
'''

    def _build_dir_metadata(self, chunk: DirChunk) -> str:
        codes = ", ".join(chunk.codes)
        imports = ", ".join(chunk.imports)
        functions = ", ".join(map(lambda tup: f"{tup[0]} in file '{tup[1]}'", chunk.functions))
        classes = ", ".join(map(lambda tup: f"{tup[0]} in file '{tup[1]}'", chunk.classes))
        return \
f'''Path: {chunk.path}
- files: {codes}
- imports: {imports}
- functions: {functions}
- classes: {classes}
'''