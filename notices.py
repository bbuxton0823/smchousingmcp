"""Public notices extractor for announcements and notices."""

import re
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin
import structlog

from config.urls import URLS, BASE_URL
from utils.web_scraper_simple import scraper
from processors.cache_manager import cache_manager
from models import PublicNotice

logger = structlog.get_logger()


class PublicNoticesExtractor:
    """Extractor for public notices and announcements."""
    
    def __init__(self):
        self.base_cache_key = "public_notices"
    
    async def get_public_notices(self, limit: Optional[int] = None, 
                               date_range_days: Optional[int] = None,
                               use_cache: bool = True) -> List[PublicNotice]:
        """Get public notices, optionally filtered by limit and date range."""
        try:
            cache_key = f"{self.base_cache_key}:limit:{limit}:days:{date_range_days}"
            
            # Check cache first
            if use_cache:
                cached_data = await cache_manager.get(cache_key)
                if cached_data:
                    logger.info("Retrieved public notices from cache", 
                               limit=limit, date_range_days=date_range_days)
                    return [PublicNotice(**notice) for notice in cached_data]
            
            # Scrape fresh data
            logger.info("Scraping public notices", limit=limit, date_range_days=date_range_days)
            notices = await self._scrape_public_notices()
            
            # Apply filters
            if date_range_days:
                cutoff_date = datetime.now() - timedelta(days=date_range_days)
                notices = [notice for notice in notices 
                          if notice.date_published and notice.date_published >= cutoff_date]
            
            if limit:
                notices = notices[:limit]
            
            # Cache the results
            if notices:
                cache_data = [notice.dict() for notice in notices]
                await cache_manager.set(cache_key, cache_data, ttl_hours=6)
                logger.info("Cached public notices", count=len(notices))
            
            return notices
            
        except Exception as e:
            logger.error("Failed to get public notices", error=str(e))
            return []
    
    async def _scrape_public_notices(self) -> List[PublicNotice]:
        """Scrape public notices from the website."""
        try:
            html_content = await scraper.get_page_content(URLS["public_notices"])
            if not html_content:
                return []
            
            soup = scraper.parse_html(html_content)
            notices = []
            
            # Find notice links
            notice_links = soup.find_all('a', href=True)
            
            for link in notice_links:
                href = link.get('href')
                title = link.get_text(strip=True)
                
                # Skip if not a notice link
                if not self._is_notice_link(href, title):
                    continue
                
                # Build full URL
                if href.startswith('http'):
                    full_url = href
                else:
                    full_url = urljoin(BASE_URL, href)
                
                # Extract notice information
                notice = await self._extract_notice_info(title, full_url, link)
                if notice:
                    notices.append(notice)
            
            # Sort by date (most recent first)
            notices.sort(key=lambda x: x.date_published or datetime.min, reverse=True)
            
            logger.info("Scraped public notices", count=len(notices))
            return notices
            
        except Exception as e:
            logger.error("Failed to scrape public notices", error=str(e))
            return []
    
    def _is_notice_link(self, href: str, title: str) -> bool:
        """Check if a link is a notice link."""
        if not href or not title:
            return False
        
        # Check for notice keywords in title
        notice_keywords = [
            'notice', 'hearing', 'amendment', 'nofa', 'environmental review',
            'public meeting', 'funding availability', 'release of funds'
        ]
        
        title_lower = title.lower()
        return any(keyword in title_lower for keyword in notice_keywords)
    
    async def _extract_notice_info(self, title: str, url: str, link_element) -> Optional[PublicNotice]:
        """Extract notice information from title and URL."""
        try:
            # Determine notice type
            notice_type = self._determine_notice_type(title)
            
            # Extract date from title
            date_published = self._extract_date_from_title(title)
            
            # Look for associated documents
            documents = []
            
            # Check if the link itself is a PDF
            if url.endswith('.pdf'):
                documents.append(url)
            
            # Create notice object
            notice = PublicNotice(
                title=title,
                date_published=date_published,
                notice_type=notice_type,
                content_url=url,
                summary=self._generate_summary(title),
                documents=documents
            )
            
            return notice
            
        except Exception as e:
            logger.warning("Failed to extract notice info", title=title, url=url, error=str(e))
            return None
    
    def _determine_notice_type(self, title: str) -> str:
        """Determine the type of notice from the title."""
        title_lower = title.lower()
        
        if 'hearing' in title_lower:
            return 'Public Hearing'
        elif 'amendment' in title_lower:
            return 'Amendment'
        elif 'nofa' in title_lower or 'funding availability' in title_lower:
            return 'NOFA'
        elif 'environmental review' in title_lower:
            return 'Environmental Review'
        elif 'meeting' in title_lower:
            return 'Public Meeting'
        elif 'release of funds' in title_lower:
            return 'Release of Funds'
        else:
            return 'General Notice'
    
    def _extract_date_from_title(self, title: str) -> Optional[datetime]:
        """Extract date from notice title."""
        try:
            # Common date patterns in titles
            date_patterns = [
                r'FY(\d{2})-(\d{2})',  # FY25-26
                r'(\d{4})-(\d{4})',    # 2024-2025
                r'(\d{4})-(\d{2})',    # 2024-25
                r'(\w+\s+\d{1,2},\s+\d{4})',  # January 15, 2025
                r'(\d{1,2}/\d{1,2}/\d{4})',   # 1/15/2025
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, title)
                if match:
                    # For fiscal year patterns, use the start year
                    if 'FY' in pattern:
                        year = 2000 + int(match.group(1))
                        return datetime(year, 7, 1)  # Fiscal year starts July 1
                    elif len(match.groups()) == 2 and match.group(1).isdigit():
                        year = int(match.group(1))
                        return datetime(year, 1, 1)
                    else:
                        # Try to parse the full date string
                        date_str = match.group(1)
                        try:
                            return datetime.strptime(date_str, '%B %d, %Y')
                        except ValueError:
                            try:
                                return datetime.strptime(date_str, '%m/%d/%Y')
                            except ValueError:
                                pass
            
            # If no date found, return None
            return None
            
        except Exception as e:
            logger.warning("Failed to extract date from title", title=title, error=str(e))
            return None
    
    def _generate_summary(self, title: str) -> str:
        """Generate a brief summary from the title."""
        # Clean up the title and create a summary
        summary = title.strip()
        
        # Remove common prefixes
        prefixes_to_remove = [
            'Notice of ', 'Notice of Public ', 'Public Notice of ',
            'Click here for: ', 'Click here for '
        ]
        
        for prefix in prefixes_to_remove:
            if summary.startswith(prefix):
                summary = summary[len(prefix):]
                break
        
        # Limit length
        if len(summary) > 200:
            summary = summary[:197] + '...'
        
        return summary
    
    async def search_notices(self, query: str, limit: int = 10) -> List[PublicNotice]:
        """Search public notices by query."""
        try:
            # Get all notices
            all_notices = await self.get_public_notices(use_cache=True)
            
            # Search in titles and summaries
            query_lower = query.lower()
            matching_notices = []
            
            for notice in all_notices:
                score = 0
                
                # Check title
                if query_lower in notice.title.lower():
                    score += 10
                
                # Check summary
                if notice.summary and query_lower in notice.summary.lower():
                    score += 5
                
                # Check notice type
                if query_lower in notice.notice_type.lower():
                    score += 3
                
                if score > 0:
                    matching_notices.append((notice, score))
            
            # Sort by relevance score
            matching_notices.sort(key=lambda x: x[1], reverse=True)
            
            # Return top results
            return [notice for notice, score in matching_notices[:limit]]
            
        except Exception as e:
            logger.error("Failed to search notices", query=query, error=str(e))
            return []
    
    async def get_notices_by_type(self, notice_type: str) -> List[PublicNotice]:
        """Get notices filtered by type."""
        try:
            all_notices = await self.get_public_notices(use_cache=True)
            
            filtered_notices = [
                notice for notice in all_notices 
                if notice.notice_type.lower() == notice_type.lower()
            ]
            
            return filtered_notices
            
        except Exception as e:
            logger.error("Failed to get notices by type", notice_type=notice_type, error=str(e))
            return []
    
    async def get_recent_notices(self, days: int = 30) -> List[PublicNotice]:
        """Get notices from the last N days."""
        return await self.get_public_notices(date_range_days=days, use_cache=True)


# Global public notices extractor instance
public_notices_extractor = PublicNoticesExtractor()

