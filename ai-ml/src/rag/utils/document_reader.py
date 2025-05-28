"""
Document Reader Utility for different file formats
"""
import PyPDF2
import logging
from pathlib import Path
from typing import Optional

class DocumentReader:
    @staticmethod
    def read_pdf(file_path: Path) -> Optional[str]:
        """Read content from PDF file"""
        try:
            content = []
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    content.append(page.extract_text())
            return '\n'.join(content)
        except Exception as e:
            logging.error(f"Error reading PDF {file_path}: {e}")
            return None

    @staticmethod
    def read_text(file_path: Path) -> Optional[str]:
        """Read content from text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logging.error(f"Error reading text file {file_path}: {e}")
            return None

    @staticmethod
    def read_file(file_path: Path) -> Optional[str]:
        """Read content from file based on extension"""
        try:
            if file_path.suffix.lower() == '.pdf':
                return DocumentReader.read_pdf(file_path)
            else:
                return DocumentReader.read_text(file_path)
        except Exception as e:
            logging.error(f"Error reading file {file_path}: {e}")
            return None