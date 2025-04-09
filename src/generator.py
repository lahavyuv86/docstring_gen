import subprocess
import json

def generate_docstring_with_ollama(code_snippet: str, config: dict, model: str) -> str:
    prompt = (
        "You're a Python docstring generator AI. Generate a clean docstring (where docstring is missing) for the following "
        "code, complying with PEP257 and all Ruff linter rules such as D100-D107, docstring should be in imperative mood (e.g., 'Return' instead of 'Returns')."
        "Print the suggested docstrings from top to bottom as it is shown in the given file. "
        "Make sure you aligned with all Ruff settings in this config: "
        f"{json.dumps(config, indent=2)}\n"
        "Code:\n"
        f"{code_snippet}\n\n"
    )

    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    docstring = result.stdout.decode("utf-8").strip()
    return docstring
