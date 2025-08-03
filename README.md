# PDFCraft - PDF Splitting and Markdown Conversion Tool

A powerful command-line tool for splitting PDF files based on bookmarks and converting them to markdown format.

## Features

- Load PDF files from local paths or internet URLs
- Split PDFs based on bookmark levels or keywords
- Save split files to specified directories
- Convert split PDFs to markdown using markitdown
- Comprehensive logging and error handling

## Installation

1. Create virtual environment:
```bash
python -m venv .venv
```

2. Activate virtual environment:
```bash
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
```bash
python -m src.main --help
```

### Examples

#### Split PDF by bookmark level
```bash
python -m src.main document.pdf --level 1 --output-dir ./splits
```

#### Split PDF by keywords
```bash
python -m src.main document.pdf --keywords "Chapter" "Section" --output-dir ./splits
```

#### Split PDF and convert to markdown
```bash
python -m src.main document.pdf --level 0 --output-dir ./splits --convert-markdown --markdown-dir ./markdown
```

#### Download PDF from URL and process
```bash
python -m src.main https://example.com/document.pdf --level 0 --output-dir ./downloads --convert-markdown
```

#### Advanced usage with logging and cleanup
```bash
python -m src.main document.pdf --keywords "Introduction" "Conclusion" --output-dir ./output --convert-markdown --log-level DEBUG --cleanup
```

## Command Line Options

- `source`: PDF file path or URL to process (required)
- `--output-dir, -o`: Directory to save split PDF files (default: ./split_pdfs)
- `--level, -l`: Maximum bookmark level to include (0-indexed)
- `--keywords, -k`: Keywords to filter bookmarks by title
- `--convert-markdown, -m`: Convert split PDFs to markdown format
- `--markdown-dir`: Directory to save markdown files (default: ./markdown)
- `--case-sensitive`: Use case-sensitive keyword matching
- `--log-level`: Set logging level (DEBUG, INFO, WARNING, ERROR)
- `--cleanup`: Clean up temporary files after processing

## Project Structure

```
PDFCraft/
├── src/
│   ├── __init__.py
│   ├── main.py              # Main entry point
│   ├── cli_handler.py       # Command line interface
│   ├── pdf_loader.py        # PDF loading from local/remote
│   ├── bookmark_analyzer.py # Bookmark analysis and filtering
│   ├── pdf_splitter.py      # PDF splitting functionality
│   └── markdown_converter.py# Markdown conversion using markitdown
├── test/
│   └── test_pdfcraft.py     # Unit tests
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## Architecture

PDFCraft follows object-oriented programming principles with high cohesion and low coupling:

- **PDFLoader**: Handles loading PDFs from local paths or URLs
- **BookmarkAnalyzer**: Extracts and filters PDF bookmarks
- **PDFSplitter**: Splits PDFs based on bookmark information
- **MarkdownConverter**: Converts PDFs to markdown using markitdown
- **CLIHandler**: Orchestrates the workflow and handles CLI

## Testing

Run the test suite:
```bash
python -m pytest test/test_pdfcraft.py -v
```

## License

MIT License
