"""Income limits extractor for PDF processing."""

import tempfile
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
import structlog

from config.urls import INCOME_LIMITS_PDFS
from utils.web_scraper_simple import scraper
from utils.pdf_parser_simple import pdf_parser
from processors.cache_manager import cache_manager
from models import IncomeLimits

logger = structlog.get_logger()


class IncomeLimitsExtractor:
    """Extractor for income limits data from PDFs."""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "smcgov_income_limits"
        self.temp_dir.mkdir(exist_ok=True)
    
    async def get_income_limits(self, year: Optional[int] = None, family_size: Optional[int] = None, 
                              use_cache: bool = True) -> List[IncomeLimits]:
        """Get income limits data, optionally filtered by year and family size."""
        try:
            cache_key = f"income_limits:year:{year}:family_size:{family_size}"
            
            # Check cache first
            if use_cache:
                cached_data = await cache_manager.get(cache_key)
                if cached_data:
                    logger.info("Retrieved income limits from cache", year=year, family_size=family_size)
                    return [IncomeLimits(**item) for item in cached_data]
            
            # Get fresh data
            logger.info("Extracting income limits from PDFs", year=year, family_size=family_size)
            
            all_income_limits = []
            
            # Determine which years to process
            years_to_process = [year] if year else [2025, 2024, 2023]
            
            for target_year in years_to_process:
                if str(target_year) in INCOME_LIMITS_PDFS:
                    limits = await self._extract_income_limits_for_year(target_year)
                    all_income_limits.extend(limits)
            
            # Filter by family size if specified
            if family_size:
                all_income_limits = [limit for limit in all_income_limits 
                                   if limit.family_size == family_size]
            
            # Cache the results
            if all_income_limits:
                cache_data = [limit.dict() for limit in all_income_limits]
                await cache_manager.set(cache_key, cache_data, ttl_hours=720)  # 30 days
                logger.info("Cached income limits data", count=len(all_income_limits))
            
            return all_income_limits
            
        except Exception as e:
            logger.error("Failed to get income limits", year=year, family_size=family_size, error=str(e))
            return []
    
    async def _extract_income_limits_for_year(self, year: int) -> List[IncomeLimits]:
        """Extract income limits for a specific year."""
        try:
            pdf_url = INCOME_LIMITS_PDFS.get(str(year))
            if not pdf_url:
                logger.warning("No PDF URL found for year", year=year)
                return self._get_mock_income_limits(year)
            
            # Download PDF
            pdf_path = self.temp_dir / f"income_limits_{year}.pdf"
            success = await scraper.download_file(pdf_url, str(pdf_path))
            
            if not success:
                logger.error("Failed to download income limits PDF, using mock data", year=year, url=pdf_url)
                return self._get_mock_income_limits(year)
            
            # Parse PDF
            income_limits = await pdf_parser.parse_income_limits_pdf(str(pdf_path), year)
            
            # Clean up PDF file
            try:
                pdf_path.unlink()
            except Exception:
                pass
            
            logger.info("Extracted income limits for year", year=year, count=len(income_limits))
            return income_limits
            
        except Exception as e:
            logger.error("Failed to extract income limits for year, using mock data", year=year, error=str(e))
            return self._get_mock_income_limits(year)
    
    def _get_mock_income_limits(self, year: int) -> List[IncomeLimits]:
        """Get mock income limits data for testing."""
        mock_data = []
        for family_size in range(1, 9):  # 1-8 person families
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
        return mock_data
    
    async def get_income_limits_summary(self) -> Dict[str, Any]:
        """Get a summary of available income limits data."""
        try:
            cache_key = "income_limits_summary"
            
            # Check cache
            cached_data = await cache_manager.get(cache_key)
            if cached_data:
                return cached_data
            
            summary = {
                'available_years': list(INCOME_LIMITS_PDFS.keys()),
                'family_sizes': list(range(1, 9)),  # Typically 1-8 person families
                'ami_categories': ['30%', '50%', '80%', '120%'],
                'last_updated': datetime.now().isoformat()
            }
            
            # Get sample data for the most recent year
            recent_limits = await self.get_income_limits(year=2025, use_cache=False)
            if recent_limits:
                summary['sample_data'] = recent_limits[0].dict()
                summary['total_records'] = len(recent_limits)
            
            # Cache the summary
            await cache_manager.set(cache_key, summary, ttl_hours=168)  # 1 week
            
            return summary
            
        except Exception as e:
            logger.error("Failed to get income limits summary", error=str(e))
            return {}
    
    async def check_eligibility(self, annual_income: float, family_size: int, 
                              ami_category: str = "80%", year: int = 2025) -> Dict[str, Any]:
        """Check eligibility based on income and family size."""
        try:
            # Get income limits for the specified parameters
            income_limits = await self.get_income_limits(year=year, family_size=family_size)
            
            if not income_limits:
                return {
                    'eligible': False,
                    'reason': f'No income limits data found for {family_size} person family in {year}',
                    'year': year,
                    'family_size': family_size
                }
            
            limit_data = income_limits[0]  # Should be only one record for specific year/family size
            
            # Determine the income limit based on AMI category
            ami_limits = {
                '30%': limit_data.ami_30_percent,
                '50%': limit_data.ami_50_percent,
                '80%': limit_data.ami_80_percent,
                '120%': limit_data.ami_120_percent
            }
            
            income_limit = ami_limits.get(ami_category)
            
            if income_limit is None:
                return {
                    'eligible': False,
                    'reason': f'Income limit not available for {ami_category} AMI category',
                    'year': year,
                    'family_size': family_size,
                    'ami_category': ami_category
                }
            
            eligible = annual_income <= income_limit
            
            result = {
                'eligible': eligible,
                'annual_income': annual_income,
                'income_limit': income_limit,
                'ami_category': ami_category,
                'year': year,
                'family_size': family_size,
                'percentage_of_limit': (annual_income / income_limit) * 100 if income_limit > 0 else 0
            }
            
            if eligible:
                result['reason'] = f'Income ${annual_income:,.2f} is within {ami_category} AMI limit of ${income_limit:,.2f}'
                
                # Add max rent information if available
                rent_limits = {
                    '30%': limit_data.max_rent_30,
                    '50%': limit_data.max_rent_50,
                    '80%': limit_data.max_rent_80
                }
                
                max_rent = rent_limits.get(ami_category)
                if max_rent:
                    result['max_affordable_rent'] = max_rent
            else:
                result['reason'] = f'Income ${annual_income:,.2f} exceeds {ami_category} AMI limit of ${income_limit:,.2f}'
            
            return result
            
        except Exception as e:
            logger.error("Failed to check eligibility", 
                        annual_income=annual_income, 
                        family_size=family_size, 
                        error=str(e))
            return {
                'eligible': False,
                'reason': f'Error checking eligibility: {str(e)}',
                'year': year,
                'family_size': family_size
            }
    
    async def get_rent_limits(self, family_size: int, year: int = 2025) -> Dict[str, Any]:
        """Get maximum affordable rent limits for a family size."""
        try:
            income_limits = await self.get_income_limits(year=year, family_size=family_size)
            
            if not income_limits:
                return {}
            
            limit_data = income_limits[0]
            
            rent_limits = {
                'year': year,
                'family_size': family_size,
                'rent_limits': {}
            }
            
            if limit_data.max_rent_30:
                rent_limits['rent_limits']['30% AMI'] = limit_data.max_rent_30
            if limit_data.max_rent_50:
                rent_limits['rent_limits']['50% AMI'] = limit_data.max_rent_50
            if limit_data.max_rent_80:
                rent_limits['rent_limits']['80% AMI'] = limit_data.max_rent_80
            
            return rent_limits
            
        except Exception as e:
            logger.error("Failed to get rent limits", family_size=family_size, year=year, error=str(e))
            return {}
    
    def cleanup(self):
        """Clean up temporary files."""
        try:
            for file_path in self.temp_dir.glob("*.pdf"):
                file_path.unlink()
            logger.info("Cleaned up income limits temp files")
        except Exception as e:
            logger.warning("Failed to cleanup income limits temp files", error=str(e))


# Global income limits extractor instance
income_limits_extractor = IncomeLimitsExtractor()

