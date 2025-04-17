# 📝 Docstring Generator using Ollama

This is a CLI tool that generates Python docstrings using a local LLM via [Ollama](https://ollama.com). It supports generating docstrings for modules, classes, and functions, and aims to comply with Ruff linting configurations specified in your `pyproject.toml`.

## ✅ Features

- Scans `.py` files and extracts functions, classes, modules
- Reads `pyproject.toml` for Ruff config
- Prompts Ollama to generate compliant docstrings
- Supports both single file and full directory

## Requirements

- Python 3.8+
- [Ollama](https://ollama.com) installed and running
- A `.gguf` model available via Ollama (e.g., `mistral`)

## Installation

```bash
git clone <your-repo-url>
cd docstring_gen
pip install -r requirements.txt
```

## 🚀 Usage

```bash
python main.py <path/to/file_or_dir> <path/to/pyproject.toml> --model <model name>
```
#### To print the generated docstrings to console add this flag:
```bash
--print
```

#### To insert the generated docstrings to the given file add this flag:
```bash
--insert
```

## License

MIT License
