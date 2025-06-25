"""Simplified PDF parsing utilities for testing."""

import re
import tempfile
from typing import List, Dict, Optional, Any
import structlog
from pathlib import Path

from models import IncomeLimits

logger = structlog.get_logger()


class PDFParser:
    """Simplified PDF parsing utility for testing."""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "smcgov_housing_pdfs"
        self.temp_dir.mkdir(exist_ok=True)
    
    async def parse_income_limits_pdf(self, pdf_path: str, year: int) -> List[IncomeLimits]:
        """Parse income limits PDF and extract structured data (mock for testing)."""
        try:
            logger.warning("PDF parsing not available, returning mock data", pdf_path=pdf_path, year=year)
            
            # Return mock data for testing
            mock_data = []
            for family_size in range(1, 5):  # 1-4 person families
                income_limit = IncomeLimits(
                    year=year,
                    family_size=family_size,
                    ami_30_percent=30000 + (family_size * 5000),
                    ami_50_percent=50000 + (family_size * 8000),
                    ami_80_percent=80000 + (family_size * 12000),
                    ami_120_percent=120000 + (family_size * 18000),
                    max_rent_30=750 + (family_size * 125),
                    max_rent_50=1250 + (family_size * 200),
                    max_rent_80=2000 + (family_size * 300)
                )
                mock_data.append(income_limit)
            
            logger.info("Generated mock income limits data", pdf_path=pdf_path, records=len(mock_data))
            return mock_data
            
        except Exception as e:
            logger.error("Failed to parse income limits PDF", pdf_path=pdf_path, error=str(e))
            return []
    
    async def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract all text from a PDF (mock for testing)."""
        try:
            logger.warning("PDF text extraction not available, returning mock text", pdf_path=pdf_path)
            return "Mock PDF content for testing purposes."
        except Exception as e:
            logger.error("Failed to extract text from PDF", pdf_path=pdf_path, error=str(e))
            return ""
    
    async def parse_notice_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Parse a public notice PDF and extract key information (mock for testing)."""
        try:
            logger.warning("PDF notice parsing not available, returning mock data", pdf_path=pdf_path)
            
            return {
                'title': 'Mock Notice Title',
                'dates': ['January 15, 2025'],
                'emails': ['housing@smcgov.org'],
                'phones': ['(650) 363-4000'],
                'full_text': 'Mock notice content for testing purposes.'
            }
            
        except Exception as e:
            logger.error("Failed to parse notice PDF", pdf_path=pdf_path, error=str(e))
            return {}
    
    def cleanup_temp_files(self):
        """Clean up temporary PDF files."""
        try:
            for file_path in self.temp_dir.glob("*.pdf"):
                file_path.unlink()
            logger.info("Cleaned up temporary PDF files")
        except Exception as e:
            logger.warning("Failed to cleanup temp files", error=str(e))


# Global PDF parser instance
pdf_parser = PDFParser()

