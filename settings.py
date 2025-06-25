"""Configuration settings for the SMC Housing MCP Server."""

import os
from typing import Optional
from pydantic import BaseModel


class Settings(BaseModel):
    """Application settings."""
    
    # Server configuration
    server_name: str = "smcgov-housing-mcp"
    server_version: str = "1.0.0"
    
    # Cache configuration
    cache_ttl_hours: int = 24
    cache_ttl_income_limits: int = 720  # 30 days
    cache_ttl_notices: int = 6
    
    # Web scraping configuration
    selenium_headless: bool = True
    request_timeout: int = 30
    request_delay: float = 1.0
    max_retries: int = 3
    
    # User agent for requests
    user_agent: str = "SMC Housing MCP Server/1.0.0"
    
    # Redis configuration (optional)
    redis_url: Optional[str] = None
    
    # Logging configuration
    log_level: str = "INFO"


# Global settings instance with environment variable overrides
settings = Settings(
    server_name=os.getenv("SMC_HOUSING_SERVER_NAME", "smcgov-housing-mcp"),
    server_version=os.getenv("SMC_HOUSING_SERVER_VERSION", "1.0.0"),
    cache_ttl_hours=int(os.getenv("SMC_HOUSING_CACHE_TTL", "24")),
    cache_ttl_income_limits=int(os.getenv("SMC_HOUSING_CACHE_TTL_INCOME_LIMITS", "720")),
    cache_ttl_notices=int(os.getenv("SMC_HOUSING_CACHE_TTL_NOTICES", "6")),
    selenium_headless=os.getenv("SMC_HOUSING_SELENIUM_HEADLESS", "true").lower() == "true",
    request_timeout=int(os.getenv("SMC_HOUSING_REQUEST_TIMEOUT", "30")),
    request_delay=float(os.getenv("SMC_HOUSING_REQUEST_DELAY", "1.0")),
    max_retries=int(os.getenv("SMC_HOUSING_MAX_RETRIES", "3")),
    user_agent=os.getenv("SMC_HOUSING_USER_AGENT", "SMC Housing MCP Server/1.0.0"),
    redis_url=os.getenv("SMC_HOUSING_REDIS_URL"),
    log_level=os.getenv("SMC_HOUSING_LOG_LEVEL", "INFO")
)

