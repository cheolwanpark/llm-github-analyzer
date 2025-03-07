import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Node
from repo import RepoFile, Repository
from dataclasses import dataclass
from typing import TypeVar, Union
from pathlib import Path
from pickle import dumps, loads

_parser = Parser(Language(tspython.language()))

@dataclass
class FunctionChunk:
    name: str
    decorator: str
    body: str

T = TypeVar('T', bound='ClassChunk')
@dataclass
class ClassChunk:
    name: str
    methods: list[FunctionChunk]
    inner_classes: list[T]
    decorator: str
    body: str

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
    
def _parse_decorated_def(node: Node) -> Union[FunctionChunk, ClassChunk]:
    assert node.type == "decorated_definition"
    decorator = node.children[0].text.decode()
    d = node.child_by_field_name("definition")
    
    if d.type == "function_definition":
        f = _parse_function_def(d)
        f.decorator = decorator
        f.body = node.text.decode()
        return f
    elif d.type == "class_definition":
        c = _parse_class_def(d)
        c.decorator = decorator
        c.body = node.text.decode()
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
        "",
        node.text.decode()
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

    with open(file.path, "rb") as f:
        code =  f.read()
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

def parse(repo: Repository) -> list[CodeChunk]:
    chunks = []
    for path in repo.files:
        f = RepoFile(Path(path))
        if not f.is_file or f.type != ".py":
            continue
        chunks.append(parse_code(f))
    return chunks
