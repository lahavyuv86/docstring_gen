import ast


def sanitize_docstring(docstring: str) -> str:
    """Sanitizes the docstring to ensure proper formatting.

    Ensures only one set of triple quotes wraps the docstring,
    removes redundant or empty sections, and aligns content.

    Args:
        docstring (str): The original generated docstring.

    Returns:
        str: A cleaned and properly formatted docstring.
    """
    # Remove stray triple quotes and extra spaces
    docstring = docstring.replace('"""', "").strip()

    # Split into lines and process each line
    lines = docstring.splitlines()
    formatted_lines = []
    in_section = False

    for line in lines:
        stripped_line = line.strip()
        if stripped_line in {"Args:", "Returns:", "Raises:"}:
            # Start a section only if it has meaningful content
            next_index = lines.index(line) + 1
            if next_index >= len(lines) or not lines[next_index].strip():
                continue
            formatted_lines.append(stripped_line)
            in_section = True
        elif in_section and not stripped_line:
            in_section = False  # End of section
        elif stripped_line:
            formatted_lines.append(stripped_line)

    # Wrap the cleaned docstring in triple quotes
    return f'"""\n{chr(10).join(formatted_lines)}\n"""'


def find_insertion_point(node: ast.AST, lines: list) -> int:
    """Finds the exact line number to insert the docstring.

    Args:
        node (ast.AST): The AST node of the target.
        lines (list): The lines of the source file.

    Returns:
        int: The line number where the docstring should be inserted.
    """
    current_line = node.lineno
    while current_line < len(lines):
        stripped_line = lines[current_line - 1].strip()
        if stripped_line and not stripped_line.startswith("@"):
            return current_line
        current_line += 1
    return node.lineno


def calculate_indentation(node: ast.AST, lines: list) -> str:
    """Calculates the correct indentation for the docstring.

    Adds 4 spaces for proper alignment within classes, methods, or functions.

    Args:
        node (ast.AST): The AST node of the target class, method, or function.
        lines (list): The lines of the source file.

    Returns:
        str: The appropriate indentation string for the docstring.
    """
    base_line = lines[node.lineno - 1]
    base_indentation = " " * (len(base_line) - len(base_line.lstrip()))
    # Add 4 spaces for proper alignment within the block
    return base_indentation + " " * 4


def insert_single_docstring(filepath: str, docstring: str, start_lineno: int) -> bool:
    """Inserts a single docstring into the file.

    Args:
        filepath (str): Path to the file to modify.
        docstring (str): The docstring content.
        start_lineno (int): Line number of the target node.

    Returns:
        bool: True if insertion was successful, False otherwise.
    """
    try:
        # Read file content
        with open(filepath, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Parse the file to find the target node
        tree = ast.parse("".join(lines))
        target_node = next(
            (node for node in ast.walk(tree) if hasattr(node, "lineno") and node.lineno == start_lineno),
            None
        )
        if not target_node:
            print(f"⚠️  Could not find target node at line {start_lineno} in {filepath}. Skipping...")
            return False

        # Sanitize the docstring
        sanitized_docstring = sanitize_docstring(docstring)

        # Find the insertion point and calculate indentation
        insertion_line = find_insertion_point(target_node, lines)
        indentation = calculate_indentation(target_node, lines)

        # Insert the sanitized docstring with proper indentation
        formatted_docstring = f"{indentation}{sanitized_docstring.replace(chr(10), chr(10) + indentation)}"

        lines.insert(insertion_line, formatted_docstring + "\n")

        # Write updated content back to the file
        with open(filepath, "w", encoding="utf-8") as file:
            file.writelines(lines)

        # Validate file by re-parsing it to ensure no syntax errors
        with open(filepath, "r", encoding="utf-8") as file:
            updated_lines = file.read()
        ast.parse(updated_lines)

        return True

    except SyntaxError as se:
        print(f"⚠️  Syntax error after insertion: {se}")
        return False
    except Exception as e:
        print(f"⚠️  Failed to insert docstring into {filepath} at line {start_lineno}. Error: {e}")
        return False


def batch_insert_docstrings(docstring_map: list):
    """Batch inserts docstrings into multiple files.

    Args:
        docstring_map (list): A list of docstring insertion data.
    """
    for entry in docstring_map:
        filepath = entry["filepath"]
        docstring = entry["docstring"]
        target_lineno = entry["start_lineno"]

        print(f"🔧 Inserting docstring at line {target_lineno} in {filepath}...")
        success = insert_single_docstring(filepath, docstring, target_lineno)
        if success:
            print(f"✅ Successfully inserted docstring at line {target_lineno} in {filepath}.")
        else:
            print(f"⚠️  Failed to insert docstring at line {target_lineno} in {filepath}.")
