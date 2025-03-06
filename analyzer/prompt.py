from repo import Repository
from parsing import parse, DirChunk
from typing import Optional
from llm import LLM
from common.analyzer import Query

def read_readme(repo: Repository) -> str:
    for child in repo.root.file_entries:
        if "README" in child.name:
            with open(child.path, "r") as f:
                return f.read()
    return ""

class Prompter:
    def __init__(self, repo: Repository, llm: LLM):
        self.repo = repo
        self.llm = llm
        self.chunks = parse(self.repo)
        self.repo_metadata = self._build_repo_metadata()
    
    def prompt(self, query: Query) -> str:
        return self.repo_metadata
    
    def _system_prompt(self) -> str:
        return \
'''You are a code analysis assistant specialized in understanding large codebases through hierarchical metadata. The metadata is organized into three levels:
Repository Level: A high-level summary of all directories in the project and README file, listing each directory’s path, imports, classes, and functions.
Directory Level: Detailed information for a specific directory, including its imports, classes (with decorators), and functions (with decorators).
File Level (Code File): Comprehensive details about a single code file, including its path, imports (with aliases and members), defined classes (with their methods, inner classes, and decorators), and functions.
Use this contextual information to generate clear, actionable answers. When a user query is received (e.g., “explain function A” or “suggest where to start for a new developer”), analyze the metadata from all three levels and provide a recommended code reading order with explanations on which files or directories to review and why.

Your response should identify the core components, point out dependencies, and suggest an efficient pathway to understand the project’s functionality.
'''

    def _build_repo_level_search_prompt(self, user_query: str) -> str:
        return \
f'''User Query: "{user_query}"
Metadata Construction Request:
Based on the repository's metadata, please identify and list all directories that are essential for processing the above query. For each relevant directory, provide the following details:
- File Path: The path of the directory
- Relevant Functions: List function names relevant to the User Query
- Relevant Classes: List class names relevant to the User Query
- Brief Description (if available): A short explanation of the component's purpose.
Output Format (in JSON):
[
{{
    path: "path/to/directory",
    functions: ["relevant_function1", "relevant_function2"],
    classes: ["relevant_class1", "relevant_class2", "relevant_class3"],
    description: "Brief explanation of the function's role."
}}
]

Only include those functions and classes that are necessary for processing the query "{user_query}" This metadata will be used to guide further analysis and prompt generation.

Repository Level Metadata:
{self.repo_metadata}
'''

    def _build_repo_metadata(self) -> str:
        dir_metadata = []
        for dir in self.chunks.dirs:
            chunk = self.chunks.load_dir_chunk(dir)
            dir_metadata.append(self._build_dir_metadata(chunk))
        joined_metadata = "".join(dir_metadata)
        return \
f'''Repository: {self.repo.id}
README:
{read_readme(self.repo)}

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