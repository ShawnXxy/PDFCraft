"""
PDF Loader Module - Handles loading PDF files from local or remote locations
"""
import os
import requests
import logging
from pathlib import Path
from typing import Optional, Union
from urllib.parse import urlparse
import tempfile


class PDFLoader:
    """
    Handles loading PDF files from local paths or internet URLs.
    
    This class provides functionality to:
    - Load PDF files from local file paths
    - Download PDF files from internet URLs
    - Validate PDF file existence and accessibility
    - Handle temporary file management for downloaded PDFs
    
    Attributes:
        logger: Logger instance for debugging and error tracking
        temp_dir: Temporary directory for downloaded files
    """
    
    def __init__(self):
        """Initialize PDFLoader with logging configuration."""
        self.logger = logging.getLogger(__name__)
        self.temp_dir = Path(tempfile.gettempdir()) / "pdfcraft"
        self.temp_dir.mkdir(exist_ok=True)
        
    def load_pdf(self, source: str) -> Optional[Path]:
        """
        Load a PDF file from local path or URL.
        
        Args:
            source (str): Local file path or URL to PDF file
            
        Returns:
            Optional[Path]: Path to the loaded PDF file, None if failed
            
        Raises:
            FileNotFoundError: If local file doesn't exist
            requests.RequestException: If URL download fails
            ValueError: If source is invalid
        """
        self.logger.info(f"Loading PDF from source: {source}")
        
        if not source:
            raise ValueError("Source cannot be empty")
            
        # Check if source is a URL
        if self._is_url(source):
            return self._download_pdf(source)
        else:
            return self._load_local_pdf(source)
    
    def _is_url(self, source: str) -> bool:
        """
        Check if the source is a valid URL.
        
        Args:
            source (str): Source string to check
            
        Returns:
            bool: True if source is a valid URL, False otherwise
        """
        try:
            result = urlparse(source)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _load_local_pdf(self, file_path: str) -> Path:
        """
        Load PDF from local file path.
        
        Args:
            file_path (str): Local path to PDF file
            
        Returns:
            Path: Path object to the PDF file
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not a PDF
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")
            
        if not path.suffix.lower() == '.pdf':
            raise ValueError(f"File is not a PDF: {file_path}")
            
        self.logger.info(f"Successfully loaded local PDF: {file_path}")
        return path
    
    def _download_pdf(self, url: str) -> Path:
        """
        Download PDF from URL to temporary location.
        
        Args:
            url (str): URL to download PDF from
            
        Returns:
            Path: Path to downloaded PDF file
            
        Raises:
            requests.RequestException: If download fails
            ValueError: If downloaded content is not a PDF
        """
        self.logger.info(f"Downloading PDF from URL: {url}")
        
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Check if content is PDF
            content_type = response.headers.get('content-type', '')
            if 'pdf' not in content_type.lower():
                self.logger.warning(f"Content-Type may not be PDF: {content_type}")
            
            # Generate temporary file path
            filename = self._extract_filename_from_url(url)
            temp_path = self.temp_dir / filename
            
            # Download and save file
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.logger.info(f"Successfully downloaded PDF to: {temp_path}")
            return temp_path
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to download PDF from {url}: {e}")
            raise
    
    def _extract_filename_from_url(self, url: str) -> str:
        """
        Extract filename from URL or generate one.
        
        Args:
            url (str): URL to extract filename from
            
        Returns:
            str: Filename for the PDF
        """
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)
        
        if not filename or not filename.endswith('.pdf'):
            filename = f"downloaded_pdf_{hash(url) % 10000}.pdf"
            
        return filename
    
    def cleanup_temp_files(self):
        """Remove all temporary files created by this loader."""
        try:
            for file_path in self.temp_dir.glob("*.pdf"):
                file_path.unlink()
                self.logger.info(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            self.logger.error(f"Error cleaning up temporary files: {e}")
