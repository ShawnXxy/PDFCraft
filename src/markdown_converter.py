"""
Markdown Converter Module - Converts PDF files to markdown using markitdown
"""
import logging
from pathlib import Path
from typing import List, Optional
from markitdown import MarkItDown


class MarkdownConverter:
    """
    Converts PDF files to markdown format using markitdown library.

    This class provides functionality to:
    - Convert individual PDF files to markdown
    - Batch convert multiple PDF files
    - Save markdown files to specified directory
    - Handle conversion errors gracefully

    Attributes:
        logger: Logger instance for debugging and error tracking
        markitdown: MarkItDown converter instance
    """

    def __init__(self):
        """Initialize MarkdownConverter with logging and markitdown setup."""
        self.logger = logging.getLogger(__name__)
        self.markitdown = MarkItDown()

    def convert_pdf_to_markdown(self, pdf_path: Path,
                                output_dir: Path) -> Optional[Path]:
        """
        Convert a single PDF file to markdown.

        Args:
            pdf_path (Path): Path to the PDF file to convert
            output_dir (Path): Directory to save the markdown file

        Returns:
            Optional[Path]: Path to created markdown file, None if failed

        Raises:
            FileNotFoundError: If PDF file doesn't exist
        """
        self.logger.info(f"Converting PDF to markdown: {pdf_path}")

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Convert PDF to markdown
            result = self.markitdown.convert(str(pdf_path))

            if result and result.text_content:
                # Generate markdown filename
                md_filename = pdf_path.stem + '.md'
                md_path = output_dir / md_filename

                # Save markdown content
                with open(md_path, 'w', encoding='utf-8') as md_file:
                    md_file.write(result.text_content)

                self.logger.info(f"Successfully converted to: {md_path}")
                return md_path
            else:
                self.logger.warning(f"No content extracted from: {pdf_path}")
                return None

        except Exception as e:
            self.logger.error(f"Error converting PDF to markdown: {e}")
            return None

    def convert_multiple_pdfs(self, pdf_paths: List[Path],
                              output_dir: Path) -> List[Path]:
        """
        Convert multiple PDF files to markdown.

        Args:
            pdf_paths (List[Path]): List of PDF file paths to convert
            output_dir (Path): Directory to save markdown files

        Returns:
            List[Path]: List of paths to created markdown files
        """
        self.logger.info(f"Converting {len(pdf_paths)} PDFs to markdown")

        converted_files = []

        for pdf_path in pdf_paths:
            try:
                md_path = self.convert_pdf_to_markdown(pdf_path, output_dir)
                if md_path:
                    converted_files.append(md_path)
            except Exception as e:
                self.logger.error(f"Failed to convert {pdf_path}: {e}")
                continue

        msg = f"Successfully converted {len(converted_files)} files"
        self.logger.info(msg)
        return converted_files

    def validate_markitdown_installation(self) -> bool:
        """
        Validate that markitdown is properly installed and working.

        Returns:
            bool: True if markitdown is working, False otherwise
        """
        try:
            # Test markitdown with a simple text
            test_result = self.markitdown.convert_stream(
                stream_content="test",
                file_extension=".txt"
            )
            return test_result is not None
        except Exception as e:
            self.logger.error(f"MarkItDown validation failed: {e}")
            return False
