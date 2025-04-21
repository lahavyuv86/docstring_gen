import ast


def count_lines_in_docstring(docstring: str) -> int:
    """Counts the number of lines in a docstring.

    Args:
        docstring (str): The docstring content.

    Returns:
        int: Number of lines in the docstring, including triple quotes.
    """
    return docstring.strip().count("\n") + 2  # Add 2 for the opening and closing triple quotes


def sanitize_docstring(docstring: str) -> str:
    """Sanitizes the docstring to ensure proper formatting.

    Removes Markdown-style markers like ```python and ``` at the start and end,
    and ensures proper wrapping with triple quotes.

    Args:
        docstring (str): The raw generated docstring.

    Returns:
        str: A properly formatted and cleaned docstring.
    """
    # Strip Markdown code block markers
    if docstring.startswith("```python") and docstring.endswith("```"):
        docstring = docstring[9:-3].strip()
    elif docstring.startswith("```") and docstring.endswith("```"):
        docstring = docstring[3:-3].strip()

    # Remove stray triple quotes and extra spaces
    docstring = docstring.replace('"""', "").strip()

    # Wrap the cleaned content in triple quotes
    return f'"""\n{docstring.strip()}\n"""'


def find_insertion_point(node: ast.AST, lines: list) -> int:
    """Finds the correct insertion point for the docstring.

    Traverses past the function/class signature to locate the start of the body,
    skipping continuation lines, comments, and decorators.

    Args:
        node (ast.AST): The AST node of the target function/class.
        lines (list): The file content split into lines.

    Returns:
        int: The line number where the docstring should be inserted.
    """
    current_line = node.lineno - 1

    # Locate the colon marking the end of the signature
    while ":\n" not in lines[current_line]:
        current_line += 1

    # Move to the next line after the colon
    current_line += 1

    # Skip empty lines, continuation lines, comments, and decorators
    while current_line < len(lines):
        stripped_line = lines[current_line].strip()
        if stripped_line and not stripped_line.startswith(("#", "\\")):
            break
        if not stripped_line.startswith("@"):
            current_line += 1

    return current_line


def calculate_indentation(node: ast.AST, lines: list) -> str:
    """Calculates the appropriate indentation for the docstring.

    Args:
        node (ast.AST): The AST node of the target function/class.
        lines (list): The file content split into lines.

    Returns:
        str: A string of spaces for proper indentation.
    """
    # Use the node's line for base indentation
    base_line = lines[node.lineno - 1]
    base_indentation = " " * (len(base_line) - len(base_line.lstrip()))
    return base_indentation + " " * 4


def batch_insert_docstrings(docstring_map: list):
    """Batch inserts docstrings into their respective files.

    Args:
        docstring_map (list): A list of dictionaries containing docstring metadata.
    """
    files_to_update = {}
    for entry in docstring_map:
        filepath = entry["filepath"]
        if filepath not in files_to_update:
            files_to_update[filepath] = []
        files_to_update[filepath].append(entry)

    for filepath, entries in files_to_update.items():
        with open(filepath, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Parse the file
        tree = ast.parse("".join(lines))

        for entry in entries:
            docstring = sanitize_docstring(entry["docstring"])
            node = next(
                (n for n in ast.walk(tree) if hasattr(n, "lineno") and n.lineno == entry["start_lineno"]),
                None
            )
            if node:
                insertion_point = find_insertion_point(node, lines)
                indentation = calculate_indentation(node, lines)
                formatted_docstring = f"{indentation}{docstring.replace(chr(10), chr(10) + indentation)}"
                lines.insert(insertion_point, formatted_docstring + "\n")

        # Write updated content back to the file
        with open(filepath, "w", encoding="utf-8") as file:
            file.writelines(lines)
