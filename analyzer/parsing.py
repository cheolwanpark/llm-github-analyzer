import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Node
from repo import RepoFile, Repository
from dataclasses import dataclass
from typing import TypeVar, Optional, Union
from common.redis import Redis
from common.analyzer import Analyzer
from pathlib import Path
from pickle import dumps, loads

_parser = Parser(Language(tspython.language()))

@dataclass
class FunctionChunk:
    name: str
    decorator: str
    code: str

T = TypeVar('T', bound='ClassChunk')
@dataclass
class ClassChunk:
    name: str
    methods: list[FunctionChunk]
    inner_classes: list[T]
    decorator: str

@dataclass
class Import:
    module: str
    alias: str
    members: list[str]

@dataclass
class CodeChunk:
    path: str
    name: str
    imports: list[Import]
    classes: list[ClassChunk]
    functions: list[FunctionChunk]

@dataclass
class DirChunk:
    path: str
    codes: list[str]
    imports: list[str]
    classes: list[(str, str)]
    functions: list[(str, str)]

def _read_file(path: str):
    with open(path, "rb") as f:
        return f.read()
    
def _parse_decorated_def(node: Node) -> Union[FunctionChunk, ClassChunk]:
    assert node.type == "decorated_definition"
    decorator = node.children[0].text.decode()
    d = node.child_by_field_name("definition")
    
    if d.type == "function_definition":
        f = _parse_function_def(d)
        f.decorator = decorator
        return f
    elif d.type == "class_definition":
        c = _parse_class_def(d)
        c.decorator = decorator
        return c

def _parse_function_def(node: Node) -> FunctionChunk:
    return FunctionChunk(
        node.child_by_field_name("name").text.decode(),
        "",
        node.text.decode()
    )

def _parse_class_def(node: Node):
    assert node.type == "class_definition"
    name = node.child_by_field_name("name").text.decode()
    body = node.child_by_field_name("body").children
    methods = []
    inner_classes = []
    for child in filter(lambda nd: nd.type == "function_definition", body):
        methods.append(_parse_function_def(child))
    for child in filter(lambda nd: nd.type == "class_definition", body):
        inner_classes.append(_parse_class_def(child))
    for child in filter(lambda nd: nd.type == "decorated_definition", body):
        chunk = _parse_decorated_def(child)
        if isinstance(chunk, FunctionChunk):
            methods.append(chunk)
        elif isinstance(chunk, ClassChunk):
            methods.append(chunk)

    return ClassChunk(
        name,
        methods,
        inner_classes,
        ""
    )

def _parse_module_name(node: Node):
    if node.type == "aliased_import":
        return node.child_by_field_name("name").text.decode(), \
               node.child_by_field_name("alias").text.decode()
    elif node.type == "dotted_name" or node.type == "relative_import":
        return node.text.decode(), ""

def parse_code(file: RepoFile) -> CodeChunk:
    assert file.is_file
    assert file.type == ".py"

    code = _read_file(file.path)
    tree = _parser.parse(code)
    imports = []
    classes = []
    functions = []

    def traverse(node: Node):
        if node.type == "class_definition":         # class
            classes.append(_parse_class_def(node))
        elif node.type == "function_definition":    # function
            functions.append(_parse_function_def(node))
        elif node.type == "import_statement":       # import X
            name, alias = _parse_module_name(node.child_by_field_name("name"))
            imports.append(Import(
                name, alias, []
            ))
        elif node.type == "import_from_statement":  # from A import B, C, ...
            name, alias = _parse_module_name(node.child_by_field_name("module_name"))
            members = list(map(
                lambda nd: nd.text.decode(),
                node.children_by_field_name("name")
            ))
            imports.append(Import(
                name, alias, members
            ))
        elif node.type == "decorated_definition":
            chunk = _parse_decorated_def(node)
            if isinstance(chunk, FunctionChunk):
                functions.append(chunk)
            elif isinstance(chunk, ClassChunk):
                classes.append(chunk)
        else:
            for child in node.children:
                traverse(child)

    traverse(tree.root_node)

    return CodeChunk(
        file.path,
        file.name,
        imports,
        classes,
        functions
    )

def parse_directory(dir: RepoFile) -> tuple[DirChunk, list[CodeChunk]]:
    assert dir.is_dir

    imports = set()
    classes = []
    functions = []
    codes = []

    for e in dir.file_entries:
        if e.type == ".py":
            r = parse_code(e)
            for i in r.imports:
                imports.add(i.module)
            for c in r.classes:
                classes.append((c.name, r.name))
            for f in r.functions:
                functions.append((f.name, r.name))
            codes.append(r)

    return DirChunk(
        dir.path,
        list(map(lambda r: r.name, codes)),
        list(imports),
        classes,
        functions,
    ), codes
    
class Chunks:
    def __init__(self):
        self.redis = Redis()
        self.analyzer = Analyzer.from_env(self.redis)
        self.dir_descriptions = []
        self.codes = []
        self.dirs = []
    
    def _save_dir_chunk(self, result: DirChunk):
        self.redis.set(self._dir_cache_key(result.path), dumps(result))
    
    def _save_code_chunk(self, result: CodeChunk):
        self.redis.set(self._code_cache_key(result.path), dumps(result))
    
    def load_dir_chunk(self, path: str) -> Optional[DirChunk]:
        s = self.redis.get(self._dir_cache_key(path), decode=False)
        return loads(s) if s is not None else None

    def load_code_chunk(self, path: str) -> Optional[CodeChunk]:
        s = self.redis.get(self._code_cache_key(path), decode=False)
        return loads(s) if s is not None else None

    def _dir_cache_key(self, path: str) -> str: 
        return f"{self.analyzer._redis_prefix}:directory:{path}"
    
    def _code_cache_key(self, path: str) -> str:
        return f"{self.analyzer._redis_prefix}:code:{path}"

def parse(repo: Repository) -> Chunks:
    chunks = Chunks()
    for dir in repo.directories:
        r, codes = parse_directory(RepoFile(Path(dir)))
        if len(codes) == 0:
            continue
        chunks._save_dir_chunk(r)
        for code_r in codes:
            chunks._save_code_chunk(code_r)
            chunks.codes.append(code_r.path)
        chunks.dirs.append(r.path)
    return chunks
