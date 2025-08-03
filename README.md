# PDFCraft - PDF Splitting and Markdown Conversion Tool

A powerful command-line tool for splitting PDF files based on bookmarks and converting them to markdown format.

## Features

- Load PDF files from local paths or internet URLs
- Split PDFs based on bookmark levels or keywords
- Save split files to specified directories
- Convert split PDFs to markdown using markitdown
- Operations-based command structure with post-processing support
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
python pdfcraft.py --help
```

### Command Structure
PDFCraft uses an operations-based command structure:
```bash
pdfcraft --ops OPERATION [operation_options] [--post POST_OPERATION [post_options]]
```

### Examples

#### Split PDF by bookmark level
```bash
python pdfcraft.py --ops split document.pdf --level 1 --output-dir ./splits
```

#### Split PDF by keywords
```bash
python pdfcraft.py --ops split document.pdf --keywords "Chapter" "Section" --output-dir ./splits
```

#### Split PDF and convert to markdown
```bash
python pdfcraft.py --ops split document.pdf --level 0 --output-dir ./splits --post tomd --markdown-dir ./markdown
```

#### Download PDF from URL and process
```bash
python pdfcraft.py --ops split https://example.com/document.pdf --level 0 --output-dir ./downloads --post tomd
```

#### Advanced usage with logging and cleanup
```bash
python pdfcraft.py --ops split document.pdf --keywords "Introduction" "Conclusion" --output-dir ./output --post tomd --log-level DEBUG --cleanup
```

## Command Line Options

- `source`: PDF file path or URL to process (positional argument)
- `--ops`: Operation to perform (required): `split` (case insensitive)
- `--post`: Post-processing operation (optional): `tomd` (case insensitive)
- `--output-dir, -o`: Directory to save split PDF files (default: ./split_pdfs)
- `--level, -l`: Maximum bookmark level to include (0-indexed)
- `--keywords, -k`: Keywords to filter bookmarks by title
- `--case-sensitive`: Use case-sensitive keyword matching
- `--cleanup`: Clean up temporary files after processing
- `--markdown-dir`: Directory to save markdown files (default: ./markdown)
- `--log-level`: Set logging level (DEBUG, INFO, WARNING, ERROR)

## Operations

### Split Operation (`--ops split`)
Splits PDF files based on bookmark structure:
- **Level-based splitting**: Use `--level` to specify maximum bookmark depth
- **Keyword-based splitting**: Use `--keywords` to filter by bookmark titles
- **Case sensitivity**: Use `--case-sensitive` for exact keyword matching

### Post-Processing Operations

#### Markdown Conversion (`--post tomd`)
Converts split PDF files to markdown format:
- Automatically processes all split PDF files
- Saves markdown files to specified directory
- Uses markitdown library for high-quality conversion

## Project Structure

```
PDFCraft/
├── src/
│   ├── __init__.py
│   ├── main.py              # Original entry point (legacy)
│   ├── cli_handler.py       # Original command line interface
│   ├── pdf_loader.py        # PDF loading from local/remote
│   ├── bookmark_analyzer.py # Bookmark analysis and filtering
│   ├── pdf_splitter.py      # PDF splitting functionality
│   └── markdown_converter.py# Markdown conversion using markitdown
├── pdfcraft.py              # New main CLI entry point
├── test/
│   └── test_pdfcraft.py     # Unit tests
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## Architecture

PDFCraft follows object-oriented programming principles with high cohesion and low coupling:

- **PDFCraftCLI**: Main CLI orchestrator for new command structure
- **PDFLoader**: Handles loading PDFs from local paths or URLs
- **BookmarkAnalyzer**: Extracts and filters PDF bookmarks
- **PDFSplitter**: Splits PDFs based on bookmark information
- **MarkdownConverter**: Converts PDFs to markdown using markitdown
- **CLIHandler**: Legacy CLI handler (maintained for compatibility)

## Testing

Run the test suite:
```bash
python -m pytest test/test_pdfcraft.py -v
```

Test the new command structure:
```bash
# Test help
python pdfcraft.py --help

# Test split operation
python pdfcraft.py --ops split sample.pdf --level 1

# Test with post-processing
python pdfcraft.py --ops split sample.pdf --level 1 --post tomd
```

## Migration from Legacy Commands

If you were using the old command structure:
```bash
# Old command
python -m src.main document.pdf --level 1 --convert-markdown

# New equivalent command
python pdfcraft.py --ops split document.pdf --level 1 --post tomd
```

The legacy commands in `src.main` are still available for backward compatibility.

## License

MIT License
