"""PDF parsing utilities for income limits and other documents."""

import re
import tempfile
from typing import List, Dict, Optional, Any
import pdfplumber
import structlog
from pathlib import Path

from models import IncomeLimits

logger = structlog.get_logger()


class PDFParser:
    """PDF parsing utility for housing documents."""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "smcgov_housing_pdfs"
        self.temp_dir.mkdir(exist_ok=True)
    
    async def parse_income_limits_pdf(self, pdf_path: str, year: int) -> List[IncomeLimits]:
        """Parse income limits PDF and extract structured data."""
        try:
            income_limits = []
            
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    # Extract tables from the page
                    tables = page.extract_tables()
                    
                    for table in tables:
                        if table and len(table) > 1:
                            # Process table data
                            parsed_data = self._parse_income_table(table, year)
                            income_limits.extend(parsed_data)
            
            logger.info("Parsed income limits PDF", pdf_path=pdf_path, records=len(income_limits))
            return income_limits
            
        except Exception as e:
            logger.error("Failed to parse income limits PDF", pdf_path=pdf_path, error=str(e))
            return []
    
    def _parse_income_table(self, table: List[List[str]], year: int) -> List[IncomeLimits]:
        """Parse a table from the income limits PDF."""
        income_limits = []
        
        try:
            # Find header row
            header_row = None
            for i, row in enumerate(table):
                if row and any('family' in str(cell).lower() for cell in row if cell):
                    header_row = i
                    break
            
            if header_row is None:
                return income_limits
            
            headers = [str(cell).strip() if cell else "" for cell in table[header_row]]
            
            # Find column indices
            family_size_col = self._find_column_index(headers, ['family', 'size', 'persons'])
            ami_30_col = self._find_column_index(headers, ['30%', '30 %', 'extremely low'])
            ami_50_col = self._find_column_index(headers, ['50%', '50 %', 'very low'])
            ami_80_col = self._find_column_index(headers, ['80%', '80 %', 'low'])
            ami_120_col = self._find_column_index(headers, ['120%', '120 %', 'moderate'])
            
            # Process data rows
            for row in table[header_row + 1:]:
                if not row or not any(row):
                    continue
                
                try:
                    # Extract family size
                    family_size_str = str(row[family_size_col] if family_size_col is not None else "")
                    family_size = self._extract_number(family_size_str)
                    
                    if family_size is None:
                        continue
                    
                    # Extract income limits
                    ami_30 = self._extract_currency(row[ami_30_col] if ami_30_col is not None else "")
                    ami_50 = self._extract_currency(row[ami_50_col] if ami_50_col is not None else "")
                    ami_80 = self._extract_currency(row[ami_80_col] if ami_80_col is not None else "")
                    ami_120 = self._extract_currency(row[ami_120_col] if ami_120_col is not None else "")
                    
                    # Calculate max rents (typically 30% of income / 12 months)
                    max_rent_30 = (ami_30 * 0.3 / 12) if ami_30 else None
                    max_rent_50 = (ami_50 * 0.3 / 12) if ami_50 else None
                    max_rent_80 = (ami_80 * 0.3 / 12) if ami_80 else None
                    
                    income_limit = IncomeLimits(
                        year=year,
                        family_size=family_size,
                        ami_30_percent=ami_30,
                        ami_50_percent=ami_50,
                        ami_80_percent=ami_80,
                        ami_120_percent=ami_120,
                        max_rent_30=max_rent_30,
                        max_rent_50=max_rent_50,
                        max_rent_80=max_rent_80
                    )
                    
                    income_limits.append(income_limit)
                    
                except Exception as e:
                    logger.warning("Failed to parse table row", row=row, error=str(e))
                    continue
        
        except Exception as e:
            logger.error("Failed to parse income table", error=str(e))
        
        return income_limits
    
    def _find_column_index(self, headers: List[str], keywords: List[str]) -> Optional[int]:
        """Find column index by matching keywords."""
        for i, header in enumerate(headers):
            header_lower = header.lower()
            for keyword in keywords:
                if keyword.lower() in header_lower:
                    return i
        return None
    
    def _extract_number(self, text: str) -> Optional[int]:
        """Extract number from text."""
        if not text:
            return None
        
        # Look for digits
        match = re.search(r'\d+', str(text))
        if match:
            try:
                return int(match.group())
            except ValueError:
                pass
        
        return None
    
    def _extract_currency(self, text: str) -> Optional[float]:
        """Extract currency amount from text."""
        if not text:
            return None
        
        # Remove currency symbols and commas
        cleaned = re.sub(r'[$,]', '', str(text))
        
        # Look for number (including decimals)
        match = re.search(r'\d+(?:\.\d{2})?', cleaned)
        if match:
            try:
                return float(match.group())
            except ValueError:
                pass
        
        return None
    
    async def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract all text from a PDF."""
        try:
            text_content = []
            
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
            
            return "\n\n".join(text_content)
            
        except Exception as e:
            logger.error("Failed to extract text from PDF", pdf_path=pdf_path, error=str(e))
            return ""
    
    async def parse_notice_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Parse a public notice PDF and extract key information."""
        try:
            text = await self.extract_text_from_pdf(pdf_path)
            
            # Extract key information using regex patterns
            title_match = re.search(r'NOTICE\s+OF\s+([^\n]+)', text, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else "Unknown Notice"
            
            # Look for dates
            date_patterns = [
                r'(\w+\s+\d{1,2},\s+\d{4})',
                r'(\d{1,2}/\d{1,2}/\d{4})',
                r'(\d{4}-\d{2}-\d{2})'
            ]
            
            dates = []
            for pattern in date_patterns:
                dates.extend(re.findall(pattern, text))
            
            # Extract contact information
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
            
            emails = re.findall(email_pattern, text)
            phones = re.findall(phone_pattern, text)
            
            return {
                'title': title,
                'dates': dates,
                'emails': emails,
                'phones': phones,
                'full_text': text
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

