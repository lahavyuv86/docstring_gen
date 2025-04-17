import ast
import os
from typing import List, Tuple


def find_targets_for_docstrings(path: str, is_single_file: bool):
    paths = [path] if is_single_file else _collect_py_files(path)
    results = []

    for filepath in paths:
        with open(filepath, "r", encoding="utf-8") as file:
            code = file.read()

        try:
            tree = ast.parse(code)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if ast.get_docstring(node):
                    continue  # Skip nodes with existing docstrings

                # Get line numbers for the node
                start_line = node.lineno
                end_line = getattr(node, 'end_lineno', None)  # Python 3.9+
                snippet = ast.get_source_segment(code, node)
                results.append({"filepath": filepath, "snippet": snippet, "type": type(node).__name__,
                                "start_lineno": start_line, "end_lineno": end_line})

    return results


def _collect_py_files(root: str) -> List[str]:
    py_files = []
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            if filename.endswith(".py"):
                py_files.append(os.path.join(dirpath, filename))
    return py_files
