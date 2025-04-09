import argparse
from src.parser import find_targets_for_docstrings
from src.generator import generate_docstring_with_ollama
from src.ruff import load_ruff_config

def main():
    parser = argparse.ArgumentParser(description="Generate docstrings using Ollama.")
    parser.add_argument("path", type=str, help="Path to file or directory to scan")
    parser.add_argument("config_path", type=str, help="Path to pyproject.toml for Ruff config")
    parser.add_argument("--model", type=str, default="llama3", help="Ollama model to use")
    args = parser.parse_args()

    config = load_ruff_config(args.config_path)
    is_single_file = args.path.endswith(".py")

    targets = find_targets_for_docstrings(args.path, is_single_file=is_single_file)

    for filepath, snippet, node_type, lineno in targets:
        print(f"\n✨ Generating docstring for {node_type} in {filepath}:{lineno}")
        docstring = generate_docstring_with_ollama(snippet, config, args.model)

        if not docstring.strip():
            print("⚠️  Empty docstring returned.")
        else:
            print(f"📄 Suggested docstring:\n{docstring}")

if __name__ == "__main__":
    main()
