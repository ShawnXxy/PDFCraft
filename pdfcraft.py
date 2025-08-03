#!/usr/bin/env python3
"""
PDFCraft - Main Command Line Entry Point

This module provides the main command line interface for PDFCraft with
the new command structure supporting operations and post-processing.

Usage:
    pdfcraft --ops split [split_options] [--post tomd [markdown_options]]
"""
import sys
import argparse
import logging
from pathlib import Path
from typing import Optional, List

# Import our existing modules
from src.pdf_loader import PDFLoader
from src.bookmark_analyzer import BookmarkAnalyzer
from src.pdf_splitter import PDFSplitter
from src.markdown_converter import MarkdownConverter


class PDFCraftCLI:
    """
    Main CLI handler for PDFCraft with new command structure.

    This class orchestrates PDF operations and post-processing based on
    user-specified operations and post-processing options.

    Attributes:
        logger: Logger instance for debugging and error tracking
        pdf_loader: PDFLoader instance for loading PDFs
        bookmark_analyzer: BookmarkAnalyzer instance for bookmark analysis
        pdf_splitter: PDFSplitter instance for splitting PDFs
        markdown_converter: MarkdownConverter instance for conversion
    """

    def __init__(self):
        """Initialize PDFCraftCLI with all required components."""
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
        Create and configure the main argument parser.

        Returns:
            argparse.ArgumentParser: Configured argument parser
        """
        parser = argparse.ArgumentParser(
            prog='pdfcraft',
            description=('PDFCraft - PDF processing tool with operations and '
                         'post-processing support'),
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Split PDF by bookmark level
  pdfcraft --ops split input.pdf --level 1 --output-dir ./splits

  # Split PDF and convert to markdown
  pdfcraft --ops split input.pdf --level 1 --output-dir ./splits \\
           --post tomd --markdown-dir ./markdown

  # Split PDF by keywords with markdown conversion
  pdfcraft --ops split input.pdf --keywords "Chapter" "Section" \\
           --output-dir ./splits --post tomd
            """
        )

        # Required operation parameter
        parser.add_argument(
            '--ops',
            required=True,
            help='Operation to perform (case insensitive): split'
        )

        # Optional post-processing parameter
        parser.add_argument(
            '--post',
            help='Post-processing operation (case insensitive): tomd'
        )

        # Conditional subparsers based on operation
        self._add_split_arguments(parser)
        self._add_markdown_arguments(parser)

        # Global options
        parser.add_argument(
            '--log-level',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
            default='INFO',
            help='Set logging level (default: INFO)'
        )

        return parser

    def _add_split_arguments(self, parser: argparse.ArgumentParser):
        """
        Add split operation specific arguments.

        Args:
            parser: The argument parser to add arguments to
        """
        # PDF source (required for split operation)
        parser.add_argument(
            'source',
            nargs='?',  # Make optional initially, validate later
            help='PDF file path or URL to process'
        )

        # Output directory for split PDFs
        parser.add_argument(
            '--output-dir', '-o',
            type=str,
            default='./split_pdfs',
            help='Directory to save split PDF files (default: ./split_pdfs)'
        )

        # Bookmark filtering options (mutually exclusive)
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

        # Additional split options
        parser.add_argument(
            '--case-sensitive',
            action='store_true',
            help='Use case-sensitive keyword matching'
        )

        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Clean up temporary files after processing'
        )

    def _add_markdown_arguments(self, parser: argparse.ArgumentParser):
        """
        Add markdown conversion specific arguments.

        Args:
            parser: The argument parser to add arguments to
        """
        parser.add_argument(
            '--markdown-dir',
            type=str,
            help='Directory to save markdown files (default: ./markdown)'
        )

    def validate_arguments(self, args: argparse.Namespace) -> bool:
        """
        Validate parsed arguments for consistency and requirements.

        Args:
            args: Parsed command line arguments

        Returns:
            bool: True if arguments are valid, False otherwise
        """
        # Validate operation
        if args.ops.lower() not in ['split']:
            self.logger.error(f"Unsupported operation: {args.ops}")
            return False

        # Validate post-processing
        if args.post and args.post.lower() not in ['tomd']:
            self.logger.error(f"Unsupported post-processing: {args.post}")
            return False

        # Validate split operation requirements
        if args.ops.lower() == 'split':
            if not args.source:
                self.logger.error("Source PDF path/URL is required for "
                                  "split operation")
                return False

            if args.level is None and not args.keywords:
                self.logger.error("Either --level or --keywords must be "
                                  "specified for split operation")
                return False

        return True

    def execute_split_operation(self, args: argparse.Namespace) -> List[Path]:
        """
        Execute PDF split operation based on arguments.

        Args:
            args: Parsed command line arguments

        Returns:
            List[Path]: List of created split PDF files
        """
        self.logger.info("Starting PDF split operation")

        # Load PDF
        pdf_path = self.pdf_loader.load_pdf(args.source)
        if not pdf_path:
            raise ValueError(f"Failed to load PDF: {args.source}")

        # Extract and filter bookmarks
        bookmarks = self.bookmark_analyzer.extract_bookmarks(pdf_path)

        if args.level is not None:
            filtered_bookmarks = self.bookmark_analyzer.filter_by_level(
                bookmarks, args.level
            )
        elif args.keywords:
            filtered_bookmarks = self.bookmark_analyzer.filter_by_keywords(
                bookmarks, args.keywords, args.case_sensitive
            )
        else:
            filtered_bookmarks = bookmarks

        # Generate split points
        split_points = self.bookmark_analyzer.get_split_points(
            filtered_bookmarks
        )

        # Split PDF
        output_dir = Path(args.output_dir)
        split_files = self.pdf_splitter.split_pdf(
            pdf_path, split_points, output_dir
        )

        self.logger.info(f"Successfully created {len(split_files)} "
                         f"split PDF files")

        # Cleanup if requested
        if args.cleanup:
            self.pdf_loader.cleanup_temp_files()

        return split_files

    def execute_markdown_conversion(self, split_files: List[Path],
                                    args: argparse.Namespace) -> List[Path]:
        """
        Execute markdown conversion post-processing.

        Args:
            split_files: List of split PDF files to convert
            args: Parsed command line arguments

        Returns:
            List[Path]: List of created markdown files
        """
        self.logger.info("Starting markdown conversion post-processing")

        # Determine output directory for markdown files
        if args.markdown_dir:
            markdown_dir = Path(args.markdown_dir)
        else:
            markdown_dir = Path('./markdown')

        # Convert PDFs to markdown
        markdown_files = self.markdown_converter.convert_multiple_pdfs(
            split_files, markdown_dir
        )

        self.logger.info(f"Successfully converted {len(markdown_files)} "
                         f"files to markdown")

        return markdown_files

    def run(self, args: Optional[List[str]] = None) -> int:
        """
        Main execution method for PDFCraft CLI.

        Args:
            args: Optional list of command line arguments

        Returns:
            int: Exit code (0 for success, non-zero for failure)
        """
        try:
            # Parse arguments
            parser = self.create_argument_parser()
            parsed_args = parser.parse_args(args)

            # Setup logging with specified level
            self.setup_logging(parsed_args.log_level)

            # Validate arguments
            if not self.validate_arguments(parsed_args):
                return 1

            self.logger.info("Starting PDFCraft processing")
            self.logger.info(f"Operation: {parsed_args.ops}")
            if parsed_args.post:
                self.logger.info(f"Post-processing: {parsed_args.post}")

            # Execute main operation
            operation = parsed_args.ops.lower()

            if operation == 'split':
                split_files = self.execute_split_operation(parsed_args)

                # Execute post-processing if specified
                if parsed_args.post and parsed_args.post.lower() == 'tomd':
                    self.execute_markdown_conversion(split_files, parsed_args)

            self.logger.info("PDFCraft processing completed successfully")
            return 0

        except KeyboardInterrupt:
            self.logger.info("Processing interrupted by user")
            return 1
        except Exception as e:
            self.logger.error(f"Error during processing: {e}")
            return 1


def main():
    """Main entry point for pdfcraft command."""
    cli = PDFCraftCLI()
    exit_code = cli.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
