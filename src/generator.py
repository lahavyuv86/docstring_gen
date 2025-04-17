import subprocess
import json
import re

def generate_docstring_with_ollama(code_snippet: str, config: dict, model: str) -> str:
    prompt = (
        "You're a Python docstring generator AI. Generate a clean, complete docstring "
        "complying with PEP257 and all Ruff linter rules (D100-D107). The docstring should include:\n"
        "1. A short description, should be in imperative mood (e.g., 'Return' instead of 'Returns').\n"
        "2. 'Args:' section (only if the function has parameters) with parameter names, types, and descriptions.\n"
        "3. 'Return:' section (only if the function has a return value) with the return type and description.\n\n"
        "Have spaces between each section in the docstring.\n\n"
        "Do not include 'Args:' or 'Return:' sections in the docstring when they are 'Args: None' or 'Return: None'.\n\n"
        "Comply with these Ruff settings:\n"
        f"{json.dumps(config, indent=2)}\n\n"
        "Code:\n"
        f"{code_snippet}\n\n"
    )

    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    raw_docstring = result.stdout.decode("utf-8").strip()

    # Extract docstring content between triple quotes ("""...""")
    match = re.search(r'"""(.*?)"""', raw_docstring, re.DOTALL)
    if match:
        docstring = match.group(1).strip()
    else:
        docstring = raw_docstring  # Fallback to raw output if no triple quotes

    # Validate and clean the docstring
    docstring = _clean_empty_sections(docstring)

    return docstring


def _clean_empty_sections(docstring: str) -> str:
    """Removes empty Args or Return sections from a docstring."""
    cleaned_lines = []
    skip_section = False
    for line in docstring.splitlines():
        # Check if the current section is empty
        if line.strip() == "Args:" or line.strip() == "Return:":
            skip_section = True
            continue
        if skip_section and not line.strip():  # Skip empty lines after an empty section header
            skip_section = False
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)
