"""
PDF Splitter Module - Splits PDF files based on bookmarks
"""
import PyPDF2
import logging
from pathlib import Path
from typing import List, Dict, Any
import re


class PDFSplitter:
    """
    Splits PDF files based on bookmark information.

    This class provides functionality to:
    - Split PDF files into separate documents based on bookmarks
    - Save split PDFs to specified output directory
    - Generate meaningful filenames for split documents
    - Handle page range validation and extraction

    Attributes:
        logger: Logger instance for debugging and error tracking
    """

    def __init__(self):
        """Initialize PDFSplitter with logging configuration."""
        self.logger = logging.getLogger(__name__)

    def split_pdf(self, pdf_path: Path, split_points: List[Dict[str, Any]],
                  output_dir: Path) -> List[Path]:
        """
        Split PDF file based on provided split points.

        Args:
            pdf_path (Path): Path to the source PDF file
            split_points (List[Dict[str, Any]]): List of split point
                                                 dictionaries
            output_dir (Path): Directory to save split PDF files

        Returns:
            List[Path]: List of paths to created split PDF files

        Raises:
            FileNotFoundError: If source PDF doesn't exist
            Exception: If splitting fails
        """
        self.logger.info(f"Splitting PDF: {pdf_path}")
        self.logger.info(f"Output directory: {output_dir}")

        if not pdf_path.exists():
            raise FileNotFoundError(f"Source PDF not found: {pdf_path}")

        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)

        split_files = []

        try:
            with open(pdf_path, 'rb') as source_file:
                source_pdf = PyPDF2.PdfReader(source_file)
                total_pages = len(source_pdf.pages)

                self.logger.info(f"Source PDF has {total_pages} pages")

                for i, split_point in enumerate(split_points):
                    try:
                        split_file = self._create_split_pdf(
                            source_pdf, split_point, output_dir, total_pages, i
                        )
                        if split_file:
                            split_files.append(split_file)
                    except Exception as e:
                        title = split_point['title']
                        msg = f"Error creating split PDF for '{title}': {e}"
                        self.logger.error(msg)
                        continue

                self.logger.info(
                    f"Successfully created {len(split_files)} split PDF files"
                )
                return split_files

        except Exception as e:
            self.logger.error(f"Error splitting PDF: {e}")
            raise

    def _create_split_pdf(self, source_pdf: PyPDF2.PdfReader,
                          split_point: Dict[str, Any], output_dir: Path,
                          total_pages: int, index: int) -> Path | None:
        """
        Create a single split PDF file from source PDF.

        Args:
            source_pdf: Source PDF reader object
            split_point: Split point dictionary with page information
            output_dir: Output directory for split files
            total_pages: Total number of pages in source PDF
            index: Index of current split for fallback naming

        Returns:
            Path | None: Path to created split PDF file, or None if failed
        """
        start_page = split_point['start_page'] - 1  # Convert to 0-indexed
        end_page = split_point.get('end_page')

        # If end_page is None (last split), use total pages
        if end_page is None:
            end_page = total_pages

        # Validate page ranges
        start_page = max(0, start_page)
        end_page = min(total_pages, end_page)

        if start_page >= end_page:
            title = split_point['title']
            msg = (f"Invalid page range for '{title}': "
                   f"{start_page+1}-{end_page}")
            self.logger.warning(msg)
            return None

        # Create output PDF
        output_pdf = PyPDF2.PdfWriter()
        
        # Add pages to output PDF with better error handling
        pages_added = 0
        for page_num in range(start_page, end_page):
            try:
                # Create a copy of the page to avoid recursion issues
                source_page = source_pdf.pages[page_num]
                
                # Try different approaches to add the page
                try:
                    output_pdf.add_page(source_page)
                    pages_added += 1
                except RecursionError:
                    # Handle maximum recursion depth
                    self.logger.warning(
                        f"Recursion limit hit for page {page_num + 1}, "
                        f"skipping this page"
                    )
                    continue
                except Exception as inner_e:
                    self.logger.warning(
                        f"Failed to add page {page_num + 1}: {inner_e}"
                    )
                    continue
                    
            except Exception as e:
                self.logger.warning(
                    f"Error accessing page {page_num + 1}: {e}"
                )
                continue
        
        # Only create file if we actually added some pages
        if pages_added == 0:
            self.logger.warning(
                f"No pages could be added for '{split_point['title']}'"
            )
            return None

        # Generate filename
        filename = self._generate_filename(split_point['title'], index)
        output_path = output_dir / filename

        # Write split PDF to file
        with open(output_path, 'wb') as output_file:
            output_pdf.write(output_file)

        self.logger.info(
            f"Created split PDF: {filename} ({pages_added} pages)"
        )

        return output_path

    def _generate_filename(self, title: str, index: int) -> str:
        """
        Generate a safe filename from bookmark title.

        Args:
            title: Bookmark title
            index: Split index for fallback naming

        Returns:
            str: Safe filename for the split PDF
        """
        # Clean title for filename
        clean_title = re.sub(r'[^\w\s-]', '', title)
        clean_title = re.sub(r'[-\s]+', '_', clean_title)
        clean_title = clean_title.strip('_')

        # Truncate if too long
        if len(clean_title) > 50:
            clean_title = clean_title[:50]

        # Use index as fallback if title is empty
        if not clean_title:
            clean_title = f"section_{index + 1:03d}"

        return f"{clean_title}.pdf"

    def validate_split_points(self, split_points: List[Dict[str, Any]],
                              total_pages: int) -> List[Dict[str, Any]]:
        """
        Validate and adjust split points based on total pages.

        Args:
            split_points: List of split point dictionaries
            total_pages: Total number of pages in source PDF

        Returns:
            List[Dict[str, Any]]: Validated split points
        """
        if not split_points:
            return []

        validated = []

        for split_point in split_points:
            # Validate start page
            start_page = max(1, split_point['start_page'])
            start_page = min(total_pages, start_page)

            # Validate end page
            end_page = split_point.get('end_page')
            if end_page is not None:
                end_page = max(start_page, end_page)
                end_page = min(total_pages, end_page)

            # Only include valid split points
            if start_page <= total_pages:
                validated_split = {
                    'title': split_point['title'],
                    'start_page': start_page,
                    'end_page': end_page,
                    'level': split_point.get('level', 0)
                }
                validated.append(validated_split)

        self.logger.info(f"Validated {len(validated)} split points")
        return validated
