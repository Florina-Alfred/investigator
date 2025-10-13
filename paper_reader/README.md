# Paper Reader

A CLI tool to search, download, convert, and summarize research papers from arXiv.org using Ollama models. PDFs are converted to markdown and summarized via an LLM.

## Features
- Search arXiv papers by query string
- Download PDFs and convert them to markdown
- Summarize papers using an Ollama model
- Save results as markdown files

## Requirements
- Python >= 3.13
- The following Python packages:
  - arxiv >= 2.2.0
  - docling >= 2.55.0
  - langchain-community >= 0.3.30
  - ollama >= 0.6.0

## Installation
1. Clone this repository:
   ```bash
   git clone $URL
   cd paper_reader
   ```
2. (Recommended) Create and activate a virtual environment:
   ```bash
   uv sync
   ```
   ```

## Usage
Run `main.py` from the project root:

```bash
uv run main.py [options]
```

### Arguments
- `-m`, `--model`   : Ollama model to use for summaries (default: hf.co/unsloth/gpt-oss-20b-GGUF:latest)
- `-q`, `--query`   : Query string for arXiv search (default: "kubernetes robotics")
- `-s`, `--single`  : arXiv ID to fetch and process a single paper
- `-d`, `--direct`  : Path to a pre-downloaded PDF file or directory to summarize (skips arXiv search)

### Example: Search and Summarize Papers
```bash
uv run main.py --query "kubernetes robotics" --model hf.co/unsloth/gpt-oss-20b-GGUF:latest
```
This will:
- Search arXiv for papers matching the query
- Download PDFs to the `downloads` folder
- Convert each PDF to markdown
- Summarize each markdown using the specified LLM
- Save summaries as markdown files with model details appended

### Example: Summarize a Single Paper by arXiv ID
```bash
uv run main.py --single 2410.18825v2
```

### Example: Summarize a Local PDF
```bash
uv run main.py --direct path/to/local_paper.pdf
```
For a directory of PDFs:
```bash
uv run main.py --direct path/to/pdf_folder
```

## Output
- Markdown files are saved in the `downloads/` directory, named after the paper title.
- Summaries are saved with filenames ending in `_summary_<model>.md`.

## Prompts
- You can customize the summarization prompt in `prompts/summarize_paper.md`.

## Notes
- Ollama must be running and accessible for model inference.
- For custom models, specify the full model path with `--model`.

