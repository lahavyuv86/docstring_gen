import argparse
import subprocess

from src.parser import find_targets_for_docstrings
from src.generator import generate_docstring_with_ollama
from src.ruff import load_ruff_config
from src.inserter import batch_insert_docstrings
from utils import verify_no_code_removals


def main():
    """Main entry point for the docstring generation tool.

    This script scans Python files or directories to identify missing docstrings,
    generates compliant docstrings using Ollama, and either prints them to the console
    or inserts them into the corresponding locations in the source code.

    Steps:
        1. Parse command-line arguments to specify the target file/directory and Ruff config.
        2. Scan the target file/directory for functions, classes, or modules missing docstrings.
        3. Generate compliant docstrings using the Ollama model.
        4. Collect generated docstrings into a map to track their locations.
        5. Print or perform batch insertion of the docstrings based on user input.

    Raises:
        Exception: If any step fails due to file I/O or execution issues.
    """
    # Step 1: Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate docstrings using Ollama.")
    parser.add_argument("path", type=str, help="Path to file or directory to scan.")
    parser.add_argument(
        "config_path", type=str, help="Path to pyproject.toml for Ruff config."
    )
    parser.add_argument(
        "--model", type=str, default="llama3", help="Ollama model to use."
    )
    parser.add_argument(
        "--insert", action="store_true", help="Insert docstrings into files."
    )
    parser.add_argument(
        "--print", action="store_true", help="Print docstrings to the console."
    )
    args = parser.parse_args()

    if not args.insert and not args.print:
        print("⚠️  Please specify either --insert or --print.")
        return

    # Step 2: Load Ruff configuration
    config = load_ruff_config(args.config_path)
    is_single_file = args.path.endswith(".py")

    # Step 3: Find targets for docstring generation
    print("\n🔍 Scanning for functions, classes, or modules missing docstrings...")
    targets = find_targets_for_docstrings(args.path, is_single_file=is_single_file)

    # Step 4: Generate docstrings without inserting them yet
    docstring_map = []  # A map to store generated docstrings with their target locations
    for target in targets:
        filepath = target["filepath"]
        snippet = target["snippet"]
        start_lineno = target["start_lineno"]

        print(
            f"\n✨ Generating docstring for {target['type']} in {filepath}:{start_lineno}..."
        )
        docstring = generate_docstring_with_ollama(snippet, config, args.model)

        if not docstring.strip():
            print("⚠️  Empty docstring returned. Skipping...")
        else:
            if args.print:
                print(
                    f"\n📄 Suggested docstring for {filepath}:{start_lineno}:\n{docstring}"
                )
            # Add the generated docstring to the map for later insertion if needed
            docstring_map.append(
                {
                    "filepath": filepath,
                    "docstring": docstring,
                    "start_lineno": start_lineno,
                }
            )

    # Step 5: Perform batch insertion of docstrings if requested
    if args.insert:
        print("\n🛠 Inserting generated docstrings into files...")
        batch_insert_docstrings(docstring_map)
        subprocess.run(["pre-commit", "run", "--files", args.path], check=False)  # Run pre-commit to fix indentation
        subprocess.run(["ruff", "format", args.path], check=False)  # Fix formatting
        verify_no_code_removals(args.path)  # Run Git diff verification
    elif args.print:
        print("\n✅ All docstrings have been generated and printed successfully.")


if __name__ == "__main__":
    main()
