# San Mateo County Housing MCP Server Design

## Overview
This document outlines the architecture and design for a Model Context Protocol (MCP) server that provides access to San Mateo County Department of Housing data without requiring a direct API.

## MCP Server Architecture

### Core Components

#### 1. MCP Server Framework
- **Protocol**: Model Context Protocol (MCP) specification
- **Language**: Python with asyncio for async operations
- **Framework**: Custom MCP server implementation
- **Transport**: JSON-RPC over stdio/HTTP

#### 2. Data Extraction Layer
- **Web Scraping**: BeautifulSoup4 + requests for HTML parsing
- **PDF Processing**: PyPDF2/pdfplumber for income limits data
- **Dashboard Data**: Selenium for dynamic content extraction
- **Caching**: Redis/file-based caching for performance

#### 3. Data Processing Layer
- **Data Normalization**: Standardize data formats across sources
- **Data Validation**: Ensure data integrity and consistency
- **Data Transformation**: Convert raw data to structured formats

#### 4. MCP Tools Implementation
- **Resource Tools**: Access to static data and documents
- **Function Tools**: Dynamic data retrieval and processing
- **Prompt Tools**: Context-aware data queries

## Data Sources and Extraction Strategy

### 1. Dashboard Data (High Priority)
**Source**: https://www.smcgov.org/housing/doh-dashboards
**Method**: Selenium WebDriver + API inspection
**Data Types**:
- Housing statistics (total units, projects)
- Funding information (county, federal amounts)
- Project status (complete, predevelopment, construction)
- Geographic distribution by city
- AMI targeting data

**Extraction Strategy**:
```python
# Inspect network requests to find underlying data APIs
# If APIs exist, use direct HTTP requests
# Otherwise, use Selenium to extract rendered data
```

### 2. Income Limits Data (High Priority)
**Source**: https://www.smcgov.org/housing/income-limits-and-rent-payments
**Method**: PDF download + parsing
**Data Types**:
- Annual income limits by family size
- Maximum affordable rent payments
- Historical data (2002-2025)

**Extraction Strategy**:
```python
# Download PDF documents
# Parse tables using pdfplumber
# Convert to structured JSON format
# Cache processed data
```

### 3. Public Notices (Medium Priority)
**Source**: https://www.smcgov.org/housing/doh-public-notices
**Method**: HTML scraping + content parsing
**Data Types**:
- Notice titles and dates
- Notice content and documents
- Meeting announcements
- Funding opportunities

### 4. Housing Programs (Medium Priority)
**Source**: Various program pages
**Method**: HTML scraping
**Data Types**:
- Program descriptions
- Eligibility requirements
- Application processes
- Contact information

### 5. Committee Information (Low Priority)
**Source**: HCDC pages
**Method**: HTML scraping
**Data Types**:
- Meeting schedules
- Agendas and minutes
- Committee members

## MCP Tools Design

### 1. Resource Tools

#### housing_statistics
- **Description**: Get current housing statistics and metrics
- **Returns**: JSON with total units, projects, funding data
- **Cache**: 24 hours

#### income_limits
- **Description**: Get income limits by year and family size
- **Parameters**: year (optional), family_size (optional)
- **Returns**: Structured income limit data
- **Cache**: 30 days

#### public_notices
- **Description**: Get recent public notices and announcements
- **Parameters**: limit (optional), date_range (optional)
- **Returns**: List of notices with metadata
- **Cache**: 6 hours

### 2. Function Tools

#### search_housing_data
- **Description**: Search across all housing data sources
- **Parameters**: query (string), data_type (optional)
- **Returns**: Relevant data matching search criteria

#### get_project_details
- **Description**: Get detailed information about specific housing projects
- **Parameters**: project_id or project_name
- **Returns**: Project details, status, funding, location

#### check_eligibility
- **Description**: Check eligibility for housing programs
- **Parameters**: income, family_size, program_type
- **Returns**: Eligibility status and requirements

### 3. Prompt Tools

#### housing_context
- **Description**: Provide context about San Mateo County housing programs
- **Returns**: Comprehensive overview for LLM context

## Technical Implementation

### 1. MCP Server Structure
```
smcgov_housing_mcp/
├── server.py              # Main MCP server implementation
├── extractors/
│   ├── dashboard.py       # Dashboard data extraction
│   ├── income_limits.py   # PDF processing for income data
│   ├── notices.py         # Public notices scraping
│   └── programs.py        # Housing programs data
├── processors/
│   ├── data_normalizer.py # Data standardization
│   └── cache_manager.py   # Caching logic
├── tools/
│   ├── resources.py       # MCP resource tools
│   ├── functions.py       # MCP function tools
│   └── prompts.py         # MCP prompt tools
├── config/
│   ├── settings.py        # Configuration management
│   └── urls.py            # Website URLs and endpoints
├── utils/
│   ├── web_scraper.py     # Common scraping utilities
│   └── pdf_parser.py      # PDF processing utilities
└── requirements.txt       # Dependencies
```

### 2. Key Dependencies
```
mcp>=1.0.0
requests>=2.31.0
beautifulsoup4>=4.12.0
selenium>=4.15.0
pdfplumber>=0.9.0
redis>=5.0.0
asyncio
aiohttp
pydantic>=2.0.0
```

### 3. Configuration Management
```python
# Environment variables for configuration
SMC_HOUSING_CACHE_TTL=3600
SMC_HOUSING_SELENIUM_HEADLESS=true
SMC_HOUSING_REDIS_URL=redis://localhost:6379
SMC_HOUSING_LOG_LEVEL=INFO
```

## Data Models

### 1. Housing Statistics
```python
class HousingStatistics(BaseModel):
    total_affordable_units: int
    total_projects: int
    county_funding: float
    federal_funding: float
    units_by_status: Dict[str, int]
    units_by_city: Dict[str, int]
    last_updated: datetime
```

### 2. Income Limits
```python
class IncomeLimits(BaseModel):
    year: int
    family_size: int
    ami_30_percent: float
    ami_50_percent: float
    ami_80_percent: float
    ami_120_percent: float
    max_rent_30: float
    max_rent_50: float
    max_rent_80: float
```

### 3. Public Notice
```python
class PublicNotice(BaseModel):
    title: str
    date_published: datetime
    notice_type: str
    content_url: str
    summary: str
    documents: List[str]
```

## Error Handling and Resilience

### 1. Network Resilience
- Retry logic with exponential backoff
- Circuit breaker pattern for failing endpoints
- Graceful degradation when data sources are unavailable

### 2. Data Validation
- Schema validation for all extracted data
- Data quality checks and alerts
- Fallback to cached data when extraction fails

### 3. Monitoring and Logging
- Structured logging for all operations
- Performance metrics collection
- Health check endpoints

## Security Considerations

### 1. Rate Limiting
- Respect website rate limits
- Implement client-side rate limiting
- Use delays between requests

### 2. User Agent and Headers
- Use appropriate user agent strings
- Rotate headers to avoid detection
- Respect robots.txt guidelines

### 3. Data Privacy
- No storage of personal information
- Anonymize any sensitive data
- Comply with data protection regulations

## Performance Optimization

### 1. Caching Strategy
- Multi-level caching (memory + Redis)
- TTL-based cache invalidation
- Cache warming for frequently accessed data

### 2. Concurrent Processing
- Async/await for I/O operations
- Connection pooling for HTTP requests
- Parallel processing for independent data sources

### 3. Data Compression
- Compress cached data
- Use efficient serialization formats
- Minimize memory footprint

## Deployment and Scaling

### 1. Container Deployment
```dockerfile
FROM python:3.11-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /app
WORKDIR /app
CMD ["python", "server.py"]
```

### 2. Environment Configuration
- Docker Compose for local development
- Kubernetes manifests for production
- Environment-specific configuration files

### 3. Monitoring and Alerting
- Health check endpoints
- Prometheus metrics
- Grafana dashboards
- Alert rules for failures

## Future Enhancements

### 1. Real-time Updates
- WebSocket connections for live data
- Webhook support for notifications
- Event-driven data updates

### 2. Advanced Analytics
- Trend analysis and forecasting
- Data visualization endpoints
- Historical data analysis

### 3. Integration Capabilities
- REST API wrapper
- GraphQL endpoint
- Webhook notifications for data changes

