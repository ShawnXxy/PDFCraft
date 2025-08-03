"""
Main entry point for PDFCraft - PDF Splitting and Markdown Conversion Tool
"""
import sys
from .cli_handler import CLIHandler


def main():
    """Main entry point for the CLI application."""
    cli = CLIHandler()
    exit_code = cli.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
