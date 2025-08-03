"""
Bookmark Analyzer Module - Analyzes and filters PDF bookmarks
"""
import PyPDF2
import logging
from pathlib import Path
from typing import List, Dict, Any


class BookmarkAnalyzer:
    """
    Analyzes PDF bookmarks and provides filtering capabilities.

    This class provides functionality to:
    - Extract bookmarks from PDF files
    - Filter bookmarks by level depth
    - Filter bookmarks by keyword matching
    - Provide bookmark hierarchy information

    Attributes:
        logger: Logger instance for debugging and error tracking
    """

    def __init__(self):
        """Initialize BookmarkAnalyzer with logging configuration."""
        self.logger = logging.getLogger(__name__)

    def extract_bookmarks(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """
        Extract all bookmarks from a PDF file.

        Args:
            pdf_path (Path): Path to the PDF file

        Returns:
            List[Dict[str, Any]]: List of bookmark dictionaries with
                                  title, page, and level

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            Exception: If PDF reading fails
        """
        self.logger.info(f"Extracting bookmarks from: {pdf_path}")

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                bookmarks = []

                if pdf_reader.outline:
                    bookmarks = self._parse_outline(
                        pdf_reader.outline, pdf_reader)
                else:
                    self.logger.warning(f"No bookmarks found in: {pdf_path}")

                self.logger.info(f"Extracted {len(bookmarks)} bookmarks")
                return bookmarks

        except Exception as e:
            self.logger.error(f"Error reading PDF bookmarks: {e}")
            raise

    def _parse_outline(self, outline: Any, pdf_reader: PyPDF2.PdfReader,
                       level: int = 0) -> List[Dict[str, Any]]:
        """
        Recursively parse PDF outline to extract bookmark information.

        Args:
            outline: PDF outline object
            pdf_reader: PDF reader instance
            level: Current bookmark level depth

        Returns:
            List[Dict[str, Any]]: List of parsed bookmarks
        """
        bookmarks = []

        # Prevent infinite recursion
        if level > 10:  # Maximum reasonable bookmark depth
            self.logger.warning(f"Maximum bookmark depth reached: {level}")
            return bookmarks

        for item in outline:
            if isinstance(item, list):
                # Nested bookmarks
                bookmarks.extend(
                    self._parse_outline(item, pdf_reader, level + 1))
            else:
                # Individual bookmark
                try:
                    # Get actual page number from bookmark
                    page_num = self._get_page_number(item, pdf_reader)
                    bookmark = {
                        'title': str(item.title),
                        'page': page_num,
                        'level': level
                    }
                    bookmarks.append(bookmark)
                    self.logger.debug(f"Parsed bookmark: {bookmark}")
                except Exception as e:
                    self.logger.warning(f"Error parsing bookmark item: {e}")
                    continue

        return bookmarks

    def _get_page_number(self, bookmark: Any,
                         pdf_reader: PyPDF2.PdfReader) -> int:
        """
        Get page number from bookmark destination.

        Args:
            bookmark: Bookmark object
            pdf_reader: PDF reader instance

        Returns:
            int: Page number (1-indexed)
        """
        try:
            # Handle PyPDF2 Destination objects
            if hasattr(bookmark, 'page') and bookmark.page is not None:
                page_ref = bookmark.page
                
                # Handle IndirectObject references
                if hasattr(page_ref, 'get_object'):
                    try:
                        page_obj = page_ref.get_object()
                        # Find this page object in the pages list
                        for i, page in enumerate(pdf_reader.pages):
                            if page == page_obj:
                                return i + 1  # Convert to 1-indexed
                    except Exception as e:
                        self.logger.debug(
                            f"Failed to resolve IndirectObject: {e}"
                        )
                
                # Handle direct page references
                if hasattr(pdf_reader, 'pages'):
                    for i, page in enumerate(pdf_reader.pages):
                        if page == page_ref:
                            return i + 1  # Convert to 1-indexed
                
                # Handle integer page numbers
                if isinstance(page_ref, int):
                    return max(1, page_ref + 1)  # Convert to 1-indexed
            
            # Try alternative destination methods
            if hasattr(bookmark, 'dest') and bookmark.dest is not None:
                dest = bookmark.dest
                if hasattr(dest, 'page') and dest.page is not None:
                    return self._get_page_number_from_ref(
                        dest.page, pdf_reader
                    )

        except Exception as e:
            self.logger.debug(f"Page number detection failed: {e}")

        # If all else fails, return page 1
        return 1
    
    def _get_page_number_from_ref(self, page_ref: Any,
                                  pdf_reader: PyPDF2.PdfReader) -> int:
        """
        Helper method to extract page number from various reference types.
        
        Args:
            page_ref: Page reference object
            pdf_reader: PDF reader instance
            
        Returns:
            int: Page number (1-indexed)
        """
        try:
            # Handle IndirectObject
            if hasattr(page_ref, 'get_object'):
                page_obj = page_ref.get_object()
                for i, page in enumerate(pdf_reader.pages):
                    if page == page_obj:
                        return i + 1
            
            # Handle direct page objects
            for i, page in enumerate(pdf_reader.pages):
                if page == page_ref:
                    return i + 1
                    
        except Exception as e:
            self.logger.debug(f"Reference resolution failed: {e}")
            
        return 1

    def filter_by_level(self, bookmarks: List[Dict[str, Any]],
                        max_level: int) -> List[Dict[str, Any]]:
        """
        Filter bookmarks by maximum level depth.

        Args:
            bookmarks: List of bookmark dictionaries
            max_level: Maximum level depth to include (0-indexed)

        Returns:
            List[Dict[str, Any]]: Filtered bookmarks
        """
        filtered = [b for b in bookmarks if b['level'] <= max_level]
        msg = f"Filtered {len(filtered)} bookmarks by level <= {max_level}"
        self.logger.info(msg)
        return filtered

    def filter_by_keywords(self, bookmarks: List[Dict[str, Any]],
                           keywords: List[str],
                           case_sensitive: bool = False
                           ) -> List[Dict[str, Any]]:
        """
        Filter bookmarks by keyword matching in titles.

        Args:
            bookmarks: List of bookmark dictionaries
            keywords: List of keywords to match
            case_sensitive: Whether to perform case-sensitive matching

        Returns:
            List[Dict[str, Any]]: Filtered bookmarks
        """
        if not keywords:
            return bookmarks

        filtered = []
        for bookmark in bookmarks:
            title = bookmark['title']
            if not case_sensitive:
                title = title.lower()
                keywords = [k.lower() for k in keywords]

            if any(keyword in title for keyword in keywords):
                filtered.append(bookmark)

        msg = f"Filtered {len(filtered)} bookmarks by keywords: {keywords}"
        self.logger.info(msg)
        return filtered

    def get_split_points(self,
                         bookmarks: List[Dict[str, Any]]
                         ) -> List[Dict[str, Any]]:
        """
        Get split points for PDF splitting based on bookmarks.

        Args:
            bookmarks: List of bookmark dictionaries

        Returns:
            List[Dict[str, Any]]: List of split points with start/end pages
        """
        if not bookmarks:
            self.logger.warning("No bookmarks provided for split points")
            return []

        # Sort bookmarks by page number and remove duplicates
        sorted_bookmarks = sorted(bookmarks, key=lambda x: x['page'])
        
        # Remove bookmarks with duplicate page numbers
        unique_bookmarks = []
        seen_pages = set()
        for bookmark in sorted_bookmarks:
            if bookmark['page'] not in seen_pages:
                unique_bookmarks.append(bookmark)
                seen_pages.add(bookmark['page'])
        
        split_points = []

        for i, bookmark in enumerate(unique_bookmarks):
            start_page = bookmark['page']
            
            # Calculate end page
            end_page = None
            if i + 1 < len(unique_bookmarks):
                next_page = unique_bookmarks[i + 1]['page']
                # Only set end page if next bookmark is on a different page
                if next_page > start_page:
                    end_page = next_page - 1
                else:
                    # Skip this bookmark if next one is on same/earlier page
                    self.logger.debug(
                        f"Skipping bookmark '{bookmark['title']}' - "
                        f"invalid page sequence: {start_page} -> {next_page}"
                    )
                    continue
            
            split_point = {
                'title': bookmark['title'],
                'start_page': start_page,
                'end_page': end_page,
                'level': bookmark['level']
            }

            split_points.append(split_point)

        self.logger.info(f"Generated {len(split_points)} valid split points")
        return split_points
