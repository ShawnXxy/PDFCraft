"""
CLI Handler Module - Handles command line interface for PDFCraft
"""
import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

from .pdf_loader import PDFLoader
from .bookmark_analyzer import BookmarkAnalyzer
from .pdf_splitter import PDFSplitter
from .markdown_converter import MarkdownConverter


class CLIHandler:
    """
    Handles command line interface and orchestrates PDF processing workflow.

    This class provides functionality to:
    - Parse command line arguments
    - Coordinate between different modules
    - Handle the complete workflow from PDF loading to markdown conversion
    - Provide user-friendly error messages and logging

    Attributes:
        logger: Logger instance for debugging and error tracking
        pdf_loader: PDFLoader instance for loading PDFs
        bookmark_analyzer: BookmarkAnalyzer instance for bookmark analysis
        pdf_splitter: PDFSplitter instance for splitting PDFs
        markdown_converter: MarkdownConverter instance for conversion
    """

    def __init__(self):
        """Initialize CLIHandler with all required components."""
        self.setup_logging()
        self.logger = logging.getLogger(__name__)

        # Initialize all components
        self.pdf_loader = PDFLoader()
        self.bookmark_analyzer = BookmarkAnalyzer()
        self.pdf_splitter = PDFSplitter()
        self.markdown_converter = MarkdownConverter()

    def setup_logging(self, level: str = "INFO"):
        """
        Setup logging configuration.

        Args:
            level (str): Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        log_level = getattr(logging, level.upper(), logging.INFO)
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('pdfcraft.log')
            ]
        )

    def create_argument_parser(self) -> argparse.ArgumentParser:
        """
        Create and configure argument parser.

        Returns:
            argparse.ArgumentParser: Configured argument parser
        """
        parser = argparse.ArgumentParser(
            description=('PDFCraft - Split PDFs by bookmarks and convert '
                         'to markdown'),
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Split PDF by bookmarks up to level 1
  python -m src.main input.pdf --level 1 --output-dir ./splits

  # Split PDF by keywords and convert to markdown
  python -m src.main input.pdf --keywords "Chapter" "Section" \\
    --output-dir ./splits --convert-markdown --markdown-dir ./markdown

  # Download and process PDF from URL
  python -m src.main https://example.com/document.pdf --level 0 \\
    --output-dir ./downloads --convert-markdown
            """
        )

        # Required argument
        parser.add_argument(
            'source',
            help='PDF file path or URL to process'
        )

        # Output directory for split PDFs
        parser.add_argument(
            '--output-dir', '-o',
            type=str,
            default='./split_pdfs',
            help='Directory to save split PDF files (default: ./split_pdfs)'
        )

        # Bookmark filtering options
        bookmark_group = parser.add_mutually_exclusive_group()
        bookmark_group.add_argument(
            '--level', '-l',
            type=int,
            help='Maximum bookmark level to include (0-indexed)'
        )
        bookmark_group.add_argument(
            '--keywords', '-k',
            nargs='+',
            help='Keywords to filter bookmarks by title'
        )

        # Markdown conversion options
        parser.add_argument(
            '--convert-markdown', '-m',
            action='store_true',
            help='Convert split PDFs to markdown format'
        )
        parser.add_argument(
            '--markdown-dir',
            type=str,
            help='Directory to save markdown files (default: ./markdown)'
        )

        # Additional options
        parser.add_argument(
            '--case-sensitive',
            action='store_true',
            help='Use case-sensitive keyword matching'
        )
        parser.add_argument(
            '--log-level',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
            default='INFO',
            help='Set logging level (default: INFO)'
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Clean up temporary files after processing'
        )

        return parser

    def run(self, args: Optional[List[str]] = None) -> int:
        """
        Run the complete PDF processing workflow.

        Args:
            args (Optional[List[str]]): Command line arguments (for testing)

        Returns:
            int: Exit code (0 for success, 1 for error)
        """
        try:
            # Parse arguments
            parser = self.create_argument_parser()
            parsed_args = parser.parse_args(args)

            # Update logging level
            self.setup_logging(parsed_args.log_level)

            self.logger.info("Starting PDFCraft processing")
            self.logger.info(f"Source: {parsed_args.source}")

            # Step 1: Load PDF
            pdf_path = self.pdf_loader.load_pdf(parsed_args.source)
            if not pdf_path:
                self.logger.error("Failed to load PDF")
                return 1

            # Step 2: Extract and filter bookmarks
            bookmarks = self.bookmark_analyzer.extract_bookmarks(pdf_path)
            if not bookmarks:
                self.logger.error("No bookmarks found in PDF")
                return 1

            # Apply filters
            if parsed_args.level is not None:
                bookmarks = self.bookmark_analyzer.filter_by_level(
                    bookmarks, parsed_args.level
                )
            elif parsed_args.keywords:
                bookmarks = self.bookmark_analyzer.filter_by_keywords(
                    bookmarks, parsed_args.keywords, parsed_args.case_sensitive
                )

            if not bookmarks:
                msg = "No bookmarks match the specified criteria"
                self.logger.error(msg)
                return 1

            # Step 3: Generate split points and split PDF
            split_points = self.bookmark_analyzer.get_split_points(bookmarks)
            output_dir = Path(parsed_args.output_dir)

            split_files = self.pdf_splitter.split_pdf(
                pdf_path, split_points, output_dir
            )

            if not split_files:
                self.logger.error("No PDF files were created")
                return 1

            msg = f"Successfully created {len(split_files)} split PDF files"
            self.logger.info(msg)

            # Step 4: Convert to markdown if requested
            if parsed_args.convert_markdown:
                markdown_dir = Path(parsed_args.markdown_dir or './markdown')
                markdown_files = self.markdown_converter.convert_multiple_pdfs(
                    split_files, markdown_dir
                )
                msg = f"Converted {len(markdown_files)} files to markdown"
                self.logger.info(msg)

            # Step 5: Cleanup if requested
            if parsed_args.cleanup:
                self.pdf_loader.cleanup_temp_files()
                self.logger.info("Cleaned up temporary files")

            self.logger.info("PDFCraft processing completed successfully")
            return 0

        except KeyboardInterrupt:
            self.logger.info("Processing interrupted by user")
            return 1
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return 1
