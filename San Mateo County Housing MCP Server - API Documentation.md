# San Mateo County Housing MCP Server - API Documentation

**Author:** Manus AI  
**Version:** 1.0.0  
**Date:** June 25, 2025

## Overview

The San Mateo County Housing MCP Server provides programmatic access to housing data from the San Mateo County Department of Housing through the Model Context Protocol (MCP). This API documentation describes all available tools, their parameters, response formats, and usage examples.

## Base Information

- **Protocol:** Model Context Protocol (MCP) 2024-11-05
- **Communication:** JSON-RPC over stdin/stdout
- **Data Format:** JSON with structured schemas
- **Authentication:** None required (public data)

## Available Tools

### Resource Tools

#### get_housing_statistics

Retrieves current housing statistics and metrics from the San Mateo County housing dashboard.

**Parameters:**
- `use_cache` (boolean, optional): Whether to use cached data. Default: `true`

**Response Schema:**
```json
{
  "total_affordable_units": 4939,
  "total_projects": 68,
  "county_funding": 305.3,
  "federal_funding": 52.6,
  "units_by_status": {
    "complete": 2875,
    "predevelopment": 1202,
    "construction": 862
  },
  "units_by_city": {
    "San Mateo": 694,
    "Redwood City": 617,
    "Daly City": 559
  },
  "last_updated": "2025-06-25T01:43:49.971238"
}
```

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "get_housing_statistics",
    "arguments": {
      "use_cache": true
    }
  }
}
```

#### get_income_limits

Retrieves income limits by year and family size from official PDF documents.

**Parameters:**
- `year` (integer, optional): Year for income limits (2023-2025). Range: 2023-2025
- `family_size` (integer, optional): Number of people in family (1-8). Range: 1-8
- `use_cache` (boolean, optional): Whether to use cached data. Default: `true`

**Response Schema:**
```json
[
  {
    "year": 2025,
    "family_size": 3,
    "ami_30_percent": 45000.0,
    "ami_50_percent": 74000.0,
    "ami_80_percent": 116000.0,
    "ami_120_percent": 174000.0,
    "max_rent_30": 1125.0,
    "max_rent_50": 1850.0,
    "max_rent_80": 2900.0
  }
]
```

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "get_income_limits",
    "arguments": {
      "year": 2025,
      "family_size": 3,
      "use_cache": true
    }
  }
}
```

#### get_public_notices

Retrieves recent public notices and announcements from the housing department.

**Parameters:**
- `limit` (integer, optional): Maximum number of notices to return. Range: 1-50, Default: 10
- `date_range_days` (integer, optional): Only return notices from the last N days. Range: 1-365
- `use_cache` (boolean, optional): Whether to use cached data. Default: `true`

**Response Schema:**
```json
[
  {
    "title": "Notice of Public Hearing - Housing Element Update",
    "date_published": "2025-01-15T00:00:00",
    "notice_type": "Public Hearing",
    "content_url": "https://www.smcgov.org/housing/notice-123",
    "summary": "Public hearing for housing element update",
    "documents": [
      "https://www.smcgov.org/housing/docs/hearing-notice.pdf"
    ]
  }
]
```

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "get_public_notices",
    "arguments": {
      "limit": 5,
      "date_range_days": 30,
      "use_cache": true
    }
  }
}
```

### Function Tools

#### search_housing_data

Searches across all housing data sources for relevant information.

**Parameters:**
- `query` (string, required): Search query
- `data_type` (string, optional): Type of data to search. Options: "all", "statistics", "income_limits", "notices", "programs". Default: "all"
- `limit` (integer, optional): Maximum number of results. Default: 10

**Response Schema:**
```json
[
  {
    "type": "notice",
    "data": {
      "title": "Housing Assistance Program",
      "content": "...",
      "url": "https://www.smcgov.org/housing/program-123"
    },
    "relevance": "high"
  }
]
```

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "search_housing_data",
    "arguments": {
      "query": "affordable housing",
      "data_type": "all",
      "limit": 5
    }
  }
}
```

#### check_eligibility

Checks eligibility for housing programs based on income and family size.

**Parameters:**
- `annual_income` (number, required): Annual household income in dollars
- `family_size` (integer, required): Number of people in family. Range: 1-8
- `ami_category` (string, optional): AMI category to check against. Options: "30%", "50%", "80%", "120%". Default: "80%"
- `year` (integer, optional): Year for income limits. Default: 2025

**Response Schema:**
```json
{
  "eligible": true,
  "annual_income": 75000,
  "income_limit": 116000.0,
  "ami_category": "80%",
  "year": 2025,
  "family_size": 3,
  "percentage_of_limit": 64.66,
  "reason": "Income $75,000.00 is within 80% AMI limit of $116,000.00",
  "max_affordable_rent": 2900.0
}
```

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "tools/call",
  "params": {
    "name": "check_eligibility",
    "arguments": {
      "annual_income": 75000,
      "family_size": 3,
      "ami_category": "80%",
      "year": 2025
    }
  }
}
```

#### get_funding_details

Retrieves detailed funding information for housing projects.

**Parameters:**
- `use_cache` (boolean, optional): Whether to use cached data. Default: `true`

**Response Schema:**
```json
{
  "county_funding": 305.3,
  "federal_funding": 52.6,
  "measure_k_leverage": 16.6,
  "total_leverage": "Private, Local, State and Federal Resources",
  "last_updated": "2025-06-25T01:43:49.971238"
}
```

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "tools/call",
  "params": {
    "name": "get_funding_details",
    "arguments": {
      "use_cache": true
    }
  }
}
```

#### search_notices

Searches public notices by keyword.

**Parameters:**
- `query` (string, required): Search query for notices
- `limit` (integer, optional): Maximum number of results. Default: 10

**Response Schema:**
```json
[
  {
    "title": "Notice of Funding Availability",
    "date_published": "2025-01-10T00:00:00",
    "notice_type": "NOFA",
    "content_url": "https://www.smcgov.org/housing/nofa-2025",
    "summary": "Funding available for affordable housing projects",
    "documents": []
  }
]
```

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "method": "tools/call",
  "params": {
    "name": "search_notices",
    "arguments": {
      "query": "funding",
      "limit": 5
    }
  }
}
```

#### get_cache_stats

Retrieves cache statistics and performance metrics.

**Parameters:** None

**Response Schema:**
```json
{
  "memory_cache_size": 5,
  "file_cache_size": 12,
  "redis_available": false
}
```

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 8,
  "method": "tools/call",
  "params": {
    "name": "get_cache_stats",
    "arguments": {}
  }
}
```

## Available Resources

### housing_context

Provides comprehensive context about San Mateo County housing programs and data.

**URI:** `smcgov://housing/housing_context`
**MIME Type:** `text/plain`

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 9,
  "method": "resources/read",
  "params": {
    "uri": "smcgov://housing/housing_context"
  }
}
```

### api_documentation

Provides documentation for available MCP tools and resources.

**URI:** `smcgov://housing/api_documentation`
**MIME Type:** `text/markdown`

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 10,
  "method": "resources/read",
  "params": {
    "uri": "smcgov://housing/api_documentation"
  }
}
```

## Error Handling

The MCP server returns standard JSON-RPC error responses for various error conditions.

### Common Error Codes

- `-32700`: Parse error (Invalid JSON)
- `-32600`: Invalid request (Invalid JSON-RPC)
- `-32601`: Method not found
- `-32602`: Invalid parameters
- `-32603`: Internal error
- `-1`: Application-specific error

### Error Response Format

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -1,
    "message": "Tool execution failed: Network timeout"
  }
}
```

## Rate Limiting

The MCP server implements rate limiting to respect the source website:

- Default delay: 1 second between requests
- Maximum retries: 3 attempts
- Timeout: 30 seconds per request

## Caching Behavior

The server implements multi-level caching to improve performance:

- **Housing Statistics**: 24 hours TTL
- **Income Limits**: 30 days TTL (720 hours)
- **Public Notices**: 6 hours TTL

Cache can be bypassed by setting `use_cache: false` in tool parameters.

## Usage Examples

### Complete Integration Example

```python
import json
import subprocess
import asyncio

class SMCHousingClient:
    def __init__(self, server_path):
        self.server_path = server_path
        self.process = None
        self.request_id = 0
    
    async def start(self):
        self.process = await asyncio.create_subprocess_exec(
            'python', self.server_path,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Initialize
        await self.send_request({
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "example-client", "version": "1.0.0"}
            }
        })
    
    async def send_request(self, request):
        self.request_id += 1
        request["jsonrpc"] = "2.0"
        request["id"] = self.request_id
        
        request_json = json.dumps(request) + '\n'
        self.process.stdin.write(request_json.encode())
        await self.process.stdin.drain()
        
        response_line = await self.process.stdout.readline()
        return json.loads(response_line.decode())
    
    async def get_housing_statistics(self):
        response = await self.send_request({
            "method": "tools/call",
            "params": {
                "name": "get_housing_statistics",
                "arguments": {}
            }
        })
        return json.loads(response["result"]["content"][0]["text"])
    
    async def check_eligibility(self, income, family_size, ami_category="80%"):
        response = await self.send_request({
            "method": "tools/call",
            "params": {
                "name": "check_eligibility",
                "arguments": {
                    "annual_income": income,
                    "family_size": family_size,
                    "ami_category": ami_category
                }
            }
        })
        return json.loads(response["result"]["content"][0]["text"])
    
    async def close(self):
        if self.process:
            self.process.terminate()
            await self.process.wait()

# Usage
async def main():
    client = SMCHousingClient('/path/to/server.py')
    await client.start()
    
    # Get housing statistics
    stats = await client.get_housing_statistics()
    print(f"Total units: {stats['total_affordable_units']}")
    
    # Check eligibility
    eligibility = await client.check_eligibility(75000, 3)
    print(f"Eligible: {eligibility['eligible']}")
    
    await client.close()

asyncio.run(main())
```

## Best Practices

1. **Use Caching**: Enable caching for production use to improve performance
2. **Handle Errors**: Implement proper error handling for network and data issues
3. **Rate Limiting**: Respect the built-in rate limiting to avoid overwhelming the source
4. **Resource Management**: Properly close connections and clean up resources
5. **Monitoring**: Monitor cache hit rates and response times for optimal performance

## Support and Updates

For technical support, bug reports, and feature requests, refer to the project documentation and issue tracking system. Regular updates ensure compatibility with source website changes and MCP protocol evolution.

