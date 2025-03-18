import tree_sitter_python as tspython
from tree_sitter import Language, Parser

import json

PY_LANGUAGE = Language(tspython.language())

parser = Parser(PY_LANGUAGE)


def read_file(file_path):
    """Read a Python file as bytes."""
    with open(file_path, "rb") as f:
        return f.read()


def extract_chunks(node, code_bytes, file_path):
    """Extract functions, classes, and their methods along with line numbers."""
    chunks = []
    imports = []
    current_class = None  # Track class scope

    def get_text(node):
        """Extract text from a node."""
        return code_bytes[node.start_byte : node.end_byte].decode()

    def traverse(node):
        """Recursive function to traverse the syntax tree."""
        nonlocal current_class

        if node.type == "class_definition":  # Class
            class_name = node.child_by_field_name("name").text.decode()
            start_line = node.start_point[0] + 1
            end_line = node.end_point[0] + 1

            class_code = get_text(node)
            chunks.append(
                {
                    "type": "class",
                    "name": class_name,
                    "start_line": start_line,
                    "end_line": end_line,
                    "code": class_code,
                    "file": file_path,
                }
            )
            current_class = class_name

        elif node.type == "function_definition":  # Function
            func_name = node.child_by_field_name("name").text.decode()
            start_line = node.start_point[0] + 1
            end_line = node.end_point[0] + 1

            func_code = get_text(node)
            chunk_data = {
                "type": "method" if current_class else "function",
                "name": func_name,
                "class": current_class if current_class else None,
                "start_line": start_line,
                "end_line": end_line,
                "code": func_code,
                "file": file_path,
            }
            chunks.append(chunk_data)

        elif node.type in ["import_statement", "import_from_statement"]:  # Imports
            imports.append(get_text(node))

        for child in node.children:
            traverse(child)

        if node.type == "class_definition":  # Reset class context after traversing
            current_class = None

    traverse(node)
    return chunks, imports


# Example Usage
file_path = "./data/train.py"  # Replace with the actual file path
code = read_file(file_path)
tree = parser.parse(code)

chunks, imports = extract_chunks(tree.root_node, code, file_path)


def save_to_json(data, filename="chunks.json"):
    """Save extracted chunks to a JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# Save to JSON
data_to_save = {"chunks": chunks, "imports": imports}
save_to_json(data_to_save)

print(f"Chunks saved to chunks.json")
