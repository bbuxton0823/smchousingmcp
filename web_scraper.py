"""Web scraping utilities for the MCP server."""

import asyncio
import time
from typing import Optional, Dict, Any, List
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import structlog

from config.settings import settings

logger = structlog.get_logger()


class WebScraper:
    """Web scraping utility class."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        self._driver = None
    
    async def get_page_content(self, url: str, use_selenium: bool = False) -> Optional[str]:
        """Get page content using requests or Selenium."""
        try:
            if use_selenium:
                return await self._get_content_selenium(url)
            else:
                return await self._get_content_requests(url)
        except Exception as e:
            logger.error("Failed to get page content", url=url, error=str(e))
            return None
    
    async def _get_content_requests(self, url: str) -> Optional[str]:
        """Get page content using requests."""
        try:
            await asyncio.sleep(settings.request_delay)
            response = self.session.get(url, timeout=settings.request_timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error("Request failed", url=url, error=str(e))
            return None
    
    async def _get_content_selenium(self, url: str) -> Optional[str]:
        """Get page content using Selenium for dynamic content."""
        driver = None
        try:
            driver = self._get_driver()
            driver.get(url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            await asyncio.sleep(3)
            
            return driver.page_source
        except (TimeoutException, WebDriverException) as e:
            logger.error("Selenium failed", url=url, error=str(e))
            return None
        finally:
            if driver:
                driver.quit()
    
    def _get_driver(self) -> webdriver.Chrome:
        """Create and configure Chrome driver."""
        options = Options()
        if settings.selenium_headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument(f'--user-agent={settings.user_agent}')
        
        return webdriver.Chrome(options=options)
    
    def parse_html(self, html_content: str) -> BeautifulSoup:
        """Parse HTML content with BeautifulSoup."""
        return BeautifulSoup(html_content, 'html.parser')
    
    async def download_file(self, url: str, save_path: str) -> bool:
        """Download a file from URL."""
        try:
            await asyncio.sleep(settings.request_delay)
            response = self.session.get(url, timeout=settings.request_timeout, stream=True)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info("File downloaded", url=url, save_path=save_path)
            return True
        except Exception as e:
            logger.error("File download failed", url=url, error=str(e))
            return False
    
    def extract_links(self, soup: BeautifulSoup, selector: str, base_url: str = "") -> List[str]:
        """Extract links from page using CSS selector."""
        links = []
        for link in soup.select(selector):
            href = link.get('href')
            if href:
                if href.startswith('http'):
                    links.append(href)
                elif base_url:
                    links.append(f"{base_url.rstrip('/')}/{href.lstrip('/')}")
        return links
    
    def extract_text(self, soup: BeautifulSoup, selector: str) -> Optional[str]:
        """Extract text content using CSS selector."""
        element = soup.select_one(selector)
        return element.get_text(strip=True) if element else None
    
    def extract_all_text(self, soup: BeautifulSoup, selector: str) -> List[str]:
        """Extract text from all matching elements."""
        elements = soup.select(selector)
        return [elem.get_text(strip=True) for elem in elements]
    
    async def retry_request(self, func, *args, **kwargs) -> Any:
        """Retry a request function with exponential backoff."""
        for attempt in range(settings.max_retries):
            try:
                result = await func(*args, **kwargs)
                if result is not None:
                    return result
            except Exception as e:
                logger.warning(
                    "Request attempt failed", 
                    attempt=attempt + 1, 
                    max_retries=settings.max_retries,
                    error=str(e)
                )
                
                if attempt < settings.max_retries - 1:
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
        
        logger.error("All retry attempts failed")
        return None
    
    def close(self):
        """Clean up resources."""
        if self.session:
            self.session.close()
        if self._driver:
            self._driver.quit()


# Global scraper instance
scraper = WebScraper()

