"""Configuration settings for SMC Housing MCP Server."""

import os
from typing import Optional

class Settings:
    """Application settings."""
    
    def __init__(self):
        self.server_name = "SMC Housing MCP Server"
        self.server_version = "1.0.0"
        self.cache_ttl = int(os.environ.get("SMC_HOUSING_CACHE_TTL", "3600"))
        self.log_level = os.environ.get("SMC_HOUSING_LOG_LEVEL", "INFO")
        self.selenium_headless = os.environ.get("SMC_HOUSING_SELENIUM_HEADLESS", "true").lower() == "true"
        self.redis_url = os.environ.get("SMC_HOUSING_REDIS_URL", "redis://localhost:6379")

# Global settings instance
settings = Settings()