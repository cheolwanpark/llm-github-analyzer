import tree_sitter_python as tspython
from tree_sitter import Language, Parser

from tree_sitter_languages import get_language, get_parser

LANGUAGE_CONFIG = {
    "python": {
        "function": "function_definition",
        "class": "class_definition",
        "import": ["import_statement", "import_from_statement"],
        "import_extract": {
            "dotted_name": lambda node: node.text.decode(),
            "aliased_import": lambda node: node.child_by_field_name(
                "name"
            ).text.decode(),
        },
    },
}

from pprint import pprint

PY_LANGUAGE = Language(tspython.language())

parser = Parser(PY_LANGUAGE)

# code = b"""
# import os
# import sys

# class MyClass:
#     def method1(self):
#         passthon


# def my_function(a, b):
#     return a + b
# """


# Read file as bytes
def read_file(file_path):
    with open(file_path, "rb") as f:
        return f.read()


# Load a Python file
file_path = "./data/src/redis.py"  # Change to your actual file
code = read_file(file_path)

# Parse the Code
tree = parser.parse(code)
root = tree.root_node


# Function to Extract Function and Class Names
def extract_functions_classes(node):
    results = {"classes": {}, "functions": [], "imports": []}
    current_class = None  # Track the current class

    depth = 0
    with open("log.txt", "w") as file:

        # Traverse Tree
        def traverse(node, depth):
            nonlocal current_class  # To track class scope
            file.write(f'{"    " * depth}{node.type}\n')
            if node.type == "class_definition":  # Class
                name = node.child_by_field_name("name").text.decode()
                results["classes"][name] = []  # Initialize empty function list
                current_class = name  # Update current class

            elif node.type == "function_definition":  # Function
                name = node.child_by_field_name("name").text.decode()
                if current_class:
                    results["classes"][current_class].append(name)  # Add under class
                else:
                    results["functions"].append(name)  # Top-level function

            elif node.type == "import_statement":
                for child in node.children:
                    if child.type == "dotted_name":
                        results["imports"].append(child.text.decode())
                    elif child.type == "aliased_import":
                        results["imports"].append(
                            child.child_by_field_name("name").text.decode()
                        )

            elif node.type == "import_from_statement":
                import_str = ""
                for child in node.children:
                    if child.type == "dotted_name":
                        import_str += child.text.decode() + " -> "
                    elif child.type == "aliased_import":
                        import_str += child.child_by_field_name("name").text.decode()
                results["imports"].append(
                    import_str[:-4]
                )  # get rid of last arrow 4 chars

            # Recur on children
            for child in node.children:
                traverse(child, depth + 1)

        traverse(root, depth)
        return results


# Run Extraction
parsed_output = extract_functions_classes(root)
pprint(parsed_output, width=80)

# Output:
# {'functions': ['my_function'], 'classes': ['MyClass'], 'imports': ['os', 'sys']}
