# San Mateo County Housing MCP Server

A Model Context Protocol (MCP) server that provides access to San Mateo County Department of Housing data without requiring a direct API. This server scrapes and processes data from the official SMC Housing website to provide structured access to housing statistics, income limits, public notices, and more.

## Features

- **Housing Statistics**: Access to dashboard data including total units, projects, and funding information
- **Income Limits**: Structured access to income limits by year and family size with eligibility checking
- **Public Notices**: Search and retrieve public notices, hearings, and announcements
- **Caching**: Multi-level caching for improved performance
- **Search**: Cross-data source search capabilities
- **MCP Compliance**: Full Model Context Protocol implementation

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Chrome/Chromium for Selenium (if not already installed):
   ```bash
   # Ubuntu/Debian
   sudo apt-get install chromium-browser
   
   # Or install Chrome
   wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
   sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
   sudo apt-get update
   sudo apt-get install google-chrome-stable
   ```

## Configuration

The server can be configured using environment variables:

```bash
# Cache settings
export SMC_HOUSING_CACHE_TTL=24
export SMC_HOUSING_REDIS_URL=redis://localhost:6379  # Optional

# Web scraping settings
export SMC_HOUSING_SELENIUM_HEADLESS=true
export SMC_HOUSING_REQUEST_TIMEOUT=30
export SMC_HOUSING_REQUEST_DELAY=1.0
export SMC_HOUSING_MAX_RETRIES=3

# Logging
export SMC_HOUSING_LOG_LEVEL=INFO
```

## Usage

### Running the MCP Server

```bash
python server.py
```

The server communicates via JSON-RPC over stdin/stdout following the MCP protocol.

### Testing

Run the test suite to verify functionality:

```bash
python test_server.py
```

### Available Tools

#### Resource Tools

1. **get_housing_statistics**
   - Get current housing statistics and metrics
   - Parameters: `use_cache` (boolean)

2. **get_income_limits**
   - Get income limits by year and family size
   - Parameters: `year` (2023-2025), `family_size` (1-8), `use_cache` (boolean)

3. **get_public_notices**
   - Get recent public notices and announcements
   - Parameters: `limit` (1-50), `date_range_days` (1-365), `use_cache` (boolean)

#### Function Tools

4. **search_housing_data**
   - Search across all housing data sources
   - Parameters: `query` (string), `data_type` (enum), `limit` (integer)

5. **check_eligibility**
   - Check eligibility for housing programs
   - Parameters: `annual_income` (number), `family_size` (integer), `ami_category` (enum), `year` (integer)

6. **get_funding_details**
   - Get detailed funding information
   - Parameters: `use_cache` (boolean)

7. **search_notices**
   - Search public notices by keyword
   - Parameters: `query` (string), `limit` (integer)

8. **get_cache_stats**
   - Get cache statistics and performance metrics
   - Parameters: none

### Example Usage with MCP Client

```python
import json

# Initialize the server
request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "my-client", "version": "1.0.0"}
    }
}

# Get housing statistics
request = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
        "name": "get_housing_statistics",
        "arguments": {"use_cache": true}
    }
}

# Check eligibility
request = {
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
        "name": "check_eligibility",
        "arguments": {
            "annual_income": 75000,
            "family_size": 3,
            "ami_category": "80%"
        }
    }
}
```

## Data Sources

The server extracts data from the following sources:

1. **Dashboard**: https://www.smcgov.org/housing/doh-dashboards
   - Housing statistics and metrics
   - Funding information
   - Project status data

2. **Income Limits**: https://www.smcgov.org/housing/income-limits-and-rent-payments
   - Annual income limits by family size
   - PDF documents for 2023-2025

3. **Public Notices**: https://www.smcgov.org/housing/doh-public-notices
   - Public hearings and meetings
   - Funding opportunities
   - Policy amendments

## Architecture

```
smcgov_housing_mcp/
├── server.py              # Main MCP server
├── models.py              # Data models
├── extractors/            # Data extraction modules
│   ├── dashboard.py       # Dashboard statistics
│   ├── income_limits.py   # Income limits from PDFs
│   └── notices.py         # Public notices
├── processors/            # Data processing
│   └── cache_manager.py   # Caching system
├── utils/                 # Utilities
│   ├── web_scraper.py     # Web scraping tools
│   └── pdf_parser.py      # PDF processing
└── config/                # Configuration
    ├── settings.py        # Application settings
    └── urls.py            # Website URLs
```

## Caching

The server implements a multi-level caching system:

1. **Memory Cache**: Fast in-memory storage for frequently accessed data
2. **Redis Cache**: Optional Redis backend for persistent caching
3. **File Cache**: Fallback file-based caching

Cache TTL (Time To Live) settings:
- Housing statistics: 24 hours
- Income limits: 30 days (720 hours)
- Public notices: 6 hours

## Error Handling

The server includes comprehensive error handling:

- Network timeouts and retries
- Data validation and schema checking
- Graceful degradation when data sources are unavailable
- Structured logging for debugging

## Performance Considerations

- Requests are rate-limited to respect the website
- Selenium is used only when necessary for dynamic content
- Data is cached aggressively to minimize requests
- Concurrent processing for independent operations

## Limitations

- Depends on the structure of the SMC Housing website
- Some data may not be available if the website is down
- PDF parsing may fail if document formats change
- Rate limiting may cause delays for large requests

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is provided as-is for educational and development purposes. Please respect the San Mateo County website's terms of service and robots.txt when using this server.

## Support

For issues and questions:
1. Check the logs for error messages
2. Verify network connectivity to smcgov.org
3. Test with the included test script
4. Review the MCP protocol documentation

## Changelog

### Version 1.0.0
- Initial release
- Basic MCP server implementation
- Dashboard, income limits, and notices extractors
- Multi-level caching system
- Comprehensive error handling

