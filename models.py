"""Data models for San Mateo County Housing data."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class HousingStatistics(BaseModel):
    """Housing statistics from the dashboard."""
    total_affordable_units: int = Field(description="Total number of affordable housing units")
    total_projects: int = Field(description="Total number of housing projects")
    county_funding: float = Field(description="Total county funding in millions")
    federal_funding: float = Field(description="Total federal funding in millions")
    units_by_status: Dict[str, int] = Field(description="Units grouped by status (complete, predevelopment, construction)")
    units_by_city: Dict[str, int] = Field(description="Units grouped by city")
    last_updated: datetime = Field(description="When this data was last updated")


class IncomeLimits(BaseModel):
    """Income limits data for a specific year and family size."""
    year: int = Field(description="Year for these income limits")
    family_size: int = Field(description="Number of people in family")
    ami_30_percent: Optional[float] = Field(description="30% AMI income limit")
    ami_50_percent: Optional[float] = Field(description="50% AMI income limit")
    ami_80_percent: Optional[float] = Field(description="80% AMI income limit")
    ami_120_percent: Optional[float] = Field(description="120% AMI income limit")
    max_rent_30: Optional[float] = Field(description="Maximum rent at 30% AMI")
    max_rent_50: Optional[float] = Field(description="Maximum rent at 50% AMI")
    max_rent_80: Optional[float] = Field(description="Maximum rent at 80% AMI")


class PublicNotice(BaseModel):
    """Public notice information."""
    title: str = Field(description="Notice title")
    date_published: Optional[datetime] = Field(description="Publication date")
    notice_type: str = Field(description="Type of notice (hearing, amendment, etc.)")
    content_url: str = Field(description="URL to full notice content")
    summary: Optional[str] = Field(description="Brief summary of the notice")
    documents: List[str] = Field(default_factory=list, description="Associated document URLs")


class HousingProgram(BaseModel):
    """Housing program information."""
    name: str = Field(description="Program name")
    description: str = Field(description="Program description")
    eligibility_requirements: List[str] = Field(default_factory=list, description="Eligibility requirements")
    application_process: Optional[str] = Field(description="How to apply")
    contact_info: Optional[str] = Field(description="Contact information")
    program_url: str = Field(description="URL for more information")


class ProjectDetails(BaseModel):
    """Detailed information about a housing project."""
    project_name: str = Field(description="Name of the project")
    location: Optional[str] = Field(description="Project location")
    status: str = Field(description="Current status (complete, predevelopment, construction)")
    total_units: Optional[int] = Field(description="Total number of units")
    affordable_units: Optional[int] = Field(description="Number of affordable units")
    funding_sources: List[str] = Field(default_factory=list, description="Funding sources")
    ami_targeting: Optional[Dict[str, int]] = Field(description="AMI targeting breakdown")


class SearchResult(BaseModel):
    """Search result item."""
    title: str = Field(description="Result title")
    content: str = Field(description="Result content/summary")
    url: str = Field(description="Source URL")
    data_type: str = Field(description="Type of data (statistics, notice, program, etc.)")
    relevance_score: float = Field(description="Relevance score for the search query")


class MCPResponse(BaseModel):
    """Standard MCP response wrapper."""
    success: bool = Field(description="Whether the operation was successful")
    data: Any = Field(description="Response data")
    message: Optional[str] = Field(description="Status message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class CacheEntry(BaseModel):
    """Cache entry model."""
    key: str = Field(description="Cache key")
    data: Any = Field(description="Cached data")
    expires_at: datetime = Field(description="Expiration timestamp")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")

