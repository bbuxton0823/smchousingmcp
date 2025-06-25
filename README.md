# San Mateo County Housing MCP Server

A Model Context Protocol (MCP) server providing access to San Mateo County Department of Housing data including housing statistics, income limits, and public notices.

## Features

- **Housing Statistics**: Current affordable housing units, projects, and funding data
- **Income Limits**: AMI-based income limits by family size and year
- **Public Notices**: Recent announcements and housing opportunities
- **Eligibility Checking**: Income-based program eligibility verification
- **Search Capabilities**: Cross-data source search functionality

## Quick Start

### Local Development

1. **Install Dependencies**
   ```bash
   pip install -r requirements_sse.txt
   ```

2. **Run Server**
   ```bash
   python sse_server.py
   ```

3. **Test Endpoints**
   - SSE Stream: `http://localhost:8000/sse`
   - API Docs: `http://localhost:8000/`
   - Health Check: `http://localhost:8000/health`

### Deploy to Railway

1. **Connect Repository**
   - Fork this repo
   - Connect to Railway
   - Deploy automatically

2. **Manual Deployment**
   ```bash
   railway login
   railway init
   railway up
   ```

## MCP Tools Available

- `get_housing_statistics` - Current housing metrics
- `get_income_limits` - Income limits by year/family size
- `get_public_notices` - Recent public notices
- `search_housing_data` - Search across all data
- `check_eligibility` - Income-based eligibility check
- `get_funding_details` - Project funding information

## Usage with ElevenLabs

1. **Deploy to Railway** (or your preferred platform)
2. **Add Custom MCP Server** in ElevenLabs:
   - **Name**: SMC Housing Data Server
   - **Server Type**: SSE
   - **Server URL**: `https://your-app.railway.app/sse`
   - **Tool Approval**: Always Ask (recommended)

## Configuration

Set environment variables:
```bash
SMC_HOUSING_CACHE_TTL=3600
SMC_HOUSING_LOG_LEVEL=INFO
SMC_HOUSING_SELENIUM_HEADLESS=true
```

## Architecture

- **MCP Server**: Core protocol implementation
- **SSE Wrapper**: Server-Sent Events for web clients
- **Data Extractors**: Web scraping for live data
- **Cache Layer**: Redis/file-based caching
- **Models**: Pydantic data validation

## License

MIT License - See LICENSE file for details