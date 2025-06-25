"""San Mateo County Housing MCP Server."""

import asyncio
import json
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Import our modules
from config.settings import settings
from extractors.dashboard import dashboard_extractor
from extractors.income_limits import income_limits_extractor
from extractors.notices import public_notices_extractor
from processors.cache_manager import cache_manager
from models import MCPResponse


class SMCHousingMCPServer:
    """San Mateo County Housing MCP Server."""
    
    def __init__(self):
        self.server_info = {
            "name": settings.server_name,
            "version": settings.server_version,
            "description": "MCP Server for San Mateo County Department of Housing data"
        }
        
        # Define available tools
        self.tools = {
            # Resource tools
            "get_housing_statistics": {
                "description": "Get current housing statistics and metrics from the dashboard",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "use_cache": {
                            "type": "boolean",
                            "description": "Whether to use cached data",
                            "default": True
                        }
                    }
                }
            },
            
            "get_income_limits": {
                "description": "Get income limits by year and family size",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "year": {
                            "type": "integer",
                            "description": "Year for income limits (2023-2025)",
                            "minimum": 2023,
                            "maximum": 2025
                        },
                        "family_size": {
                            "type": "integer",
                            "description": "Number of people in family (1-8)",
                            "minimum": 1,
                            "maximum": 8
                        },
                        "use_cache": {
                            "type": "boolean",
                            "description": "Whether to use cached data",
                            "default": True
                        }
                    }
                }
            },
            
            "get_public_notices": {
                "description": "Get recent public notices and announcements",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of notices to return",
                            "minimum": 1,
                            "maximum": 50,
                            "default": 10
                        },
                        "date_range_days": {
                            "type": "integer",
                            "description": "Only return notices from the last N days",
                            "minimum": 1,
                            "maximum": 365
                        },
                        "use_cache": {
                            "type": "boolean",
                            "description": "Whether to use cached data",
                            "default": True
                        }
                    }
                }
            },
            
            # Function tools
            "search_housing_data": {
                "description": "Search across all housing data sources",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "data_type": {
                            "type": "string",
                            "description": "Type of data to search",
                            "enum": ["all", "statistics", "income_limits", "notices", "programs"]
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            },
            
            "check_eligibility": {
                "description": "Check eligibility for housing programs based on income and family size",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "annual_income": {
                            "type": "number",
                            "description": "Annual household income in dollars"
                        },
                        "family_size": {
                            "type": "integer",
                            "description": "Number of people in family",
                            "minimum": 1,
                            "maximum": 8
                        },
                        "ami_category": {
                            "type": "string",
                            "description": "AMI category to check against",
                            "enum": ["30%", "50%", "80%", "120%"],
                            "default": "80%"
                        },
                        "year": {
                            "type": "integer",
                            "description": "Year for income limits",
                            "default": 2025
                        }
                    },
                    "required": ["annual_income", "family_size"]
                }
            },
            
            "get_funding_details": {
                "description": "Get detailed funding information for housing projects",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "use_cache": {
                            "type": "boolean",
                            "description": "Whether to use cached data",
                            "default": True
                        }
                    }
                }
            },
            
            "search_notices": {
                "description": "Search public notices by keyword",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for notices"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            },
            
            "get_cache_stats": {
                "description": "Get cache statistics and performance metrics",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
        
        # Define available resources
        self.resources = {
            "housing_context": {
                "description": "Comprehensive context about San Mateo County housing programs and data",
                "mimeType": "text/plain"
            },
            "api_documentation": {
                "description": "Documentation for available MCP tools and resources",
                "mimeType": "text/markdown"
            }
        }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests."""
        try:
            method = request.get("method")
            params = request.get("params", {})
            
            logger.info("Handling MCP request", method=method)
            
            if method == "initialize":
                return await self._handle_initialize(params)
            elif method == "tools/list":
                return await self._handle_tools_list()
            elif method == "tools/call":
                return await self._handle_tool_call(params)
            elif method == "resources/list":
                return await self._handle_resources_list()
            elif method == "resources/read":
                return await self._handle_resource_read(params)
            else:
                return self._error_response(f"Unknown method: {method}")
                
        except Exception as e:
            logger.error("Error handling request", error=str(e))
            return self._error_response(str(e))
    
    async def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialization request."""
        return {
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {}
                },
                "serverInfo": self.server_info
            }
        }
    
    async def _handle_tools_list(self) -> Dict[str, Any]:
        """Handle tools list request."""
        tools_list = []
        for name, tool_def in self.tools.items():
            tools_list.append({
                "name": name,
                "description": tool_def["description"],
                "inputSchema": tool_def["parameters"]
            })
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "tools": tools_list
            }
        }
    
    async def _handle_tool_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool call request."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name not in self.tools:
            return self._error_response(f"Unknown tool: {tool_name}")
        
        try:
            result = await self._execute_tool(tool_name, arguments)
            
            return {
                "jsonrpc": "2.0",
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2, default=str)
                        }
                    ]
                }
            }
            
        except Exception as e:
            logger.error("Tool execution failed", tool=tool_name, error=str(e))
            return self._error_response(f"Tool execution failed: {str(e)}")
    
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a specific tool."""
        if tool_name == "get_housing_statistics":
            use_cache = arguments.get("use_cache", True)
            stats = await dashboard_extractor.get_housing_statistics(use_cache=use_cache)
            return stats.dict() if stats else None
        
        elif tool_name == "get_income_limits":
            year = arguments.get("year")
            family_size = arguments.get("family_size")
            use_cache = arguments.get("use_cache", True)
            limits = await income_limits_extractor.get_income_limits(
                year=year, family_size=family_size, use_cache=use_cache
            )
            return [limit.dict() for limit in limits]
        
        elif tool_name == "get_public_notices":
            limit = arguments.get("limit", 10)
            date_range_days = arguments.get("date_range_days")
            use_cache = arguments.get("use_cache", True)
            notices = await public_notices_extractor.get_public_notices(
                limit=limit, date_range_days=date_range_days, use_cache=use_cache
            )
            return [notice.dict() for notice in notices]
        
        elif tool_name == "search_housing_data":
            query = arguments["query"]
            data_type = arguments.get("data_type", "all")
            limit = arguments.get("limit", 10)
            return await self._search_all_data(query, data_type, limit)
        
        elif tool_name == "check_eligibility":
            annual_income = arguments["annual_income"]
            family_size = arguments["family_size"]
            ami_category = arguments.get("ami_category", "80%")
            year = arguments.get("year", 2025)
            return await income_limits_extractor.check_eligibility(
                annual_income, family_size, ami_category, year
            )
        
        elif tool_name == "get_funding_details":
            use_cache = arguments.get("use_cache", True)
            return await dashboard_extractor.get_funding_details()
        
        elif tool_name == "search_notices":
            query = arguments["query"]
            limit = arguments.get("limit", 10)
            notices = await public_notices_extractor.search_notices(query, limit)
            return [notice.dict() for notice in notices]
        
        elif tool_name == "get_cache_stats":
            return await cache_manager.get_cache_stats()
        
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _search_all_data(self, query: str, data_type: str, limit: int) -> List[Dict[str, Any]]:
        """Search across all data sources."""
        results = []
        
        try:
            if data_type in ["all", "notices"]:
                notices = await public_notices_extractor.search_notices(query, limit)
                for notice in notices:
                    results.append({
                        "type": "notice",
                        "data": notice.dict(),
                        "relevance": "high"
                    })
            
            if data_type in ["all", "statistics"] and len(results) < limit:
                stats = await dashboard_extractor.get_housing_statistics()
                if stats and query.lower() in str(stats.dict()).lower():
                    results.append({
                        "type": "statistics",
                        "data": stats.dict(),
                        "relevance": "medium"
                    })
            
            return results[:limit]
            
        except Exception as e:
            logger.error("Search failed", query=query, error=str(e))
            return []
    
    async def _handle_resources_list(self) -> Dict[str, Any]:
        """Handle resources list request."""
        resources_list = []
        for name, resource_def in self.resources.items():
            resources_list.append({
                "uri": f"smcgov://housing/{name}",
                "name": name,
                "description": resource_def["description"],
                "mimeType": resource_def["mimeType"]
            })
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "resources": resources_list
            }
        }
    
    async def _handle_resource_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resource read request."""
        uri = params.get("uri", "")
        
        if uri == "smcgov://housing/housing_context":
            content = await self._get_housing_context()
        elif uri == "smcgov://housing/api_documentation":
            content = await self._get_api_documentation()
        else:
            return self._error_response(f"Unknown resource: {uri}")
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "text/plain",
                        "text": content
                    }
                ]
            }
        }
    
    async def _get_housing_context(self) -> str:
        """Get comprehensive housing context."""
        context = f"""
San Mateo County Department of Housing - Data Context

The San Mateo County Department of Housing provides various programs and services
to address housing needs in the county. This MCP server provides access to:

1. Housing Statistics:
   - Total affordable housing units and projects
   - Funding information (county and federal)
   - Project status breakdown
   - Geographic distribution

2. Income Limits:
   - Annual income limits by family size
   - Area Median Income (AMI) categories: 30%, 50%, 80%, 120%
   - Maximum affordable rent calculations
   - Historical data from 2023-2025

3. Public Notices:
   - Public hearings and meetings
   - Funding opportunities (NOFAs)
   - Environmental reviews
   - Policy amendments

4. Eligibility Checking:
   - Income-based eligibility for housing programs
   - Rent affordability calculations
   - AMI category determination

Data is updated regularly and cached for performance. Use the available tools
to access specific information or search across all data sources.

Server: {self.server_info['name']} v{self.server_info['version']}
Last updated: {datetime.now().isoformat()}
        """
        return context.strip()
    
    async def _get_api_documentation(self) -> str:
        """Get API documentation."""
        doc = "# San Mateo County Housing MCP Server API\n\n"
        doc += "## Available Tools\n\n"
        
        for name, tool_def in self.tools.items():
            doc += f"### {name}\n"
            doc += f"{tool_def['description']}\n\n"
            doc += "**Parameters:**\n"
            
            properties = tool_def['parameters'].get('properties', {})
            for param_name, param_def in properties.items():
                doc += f"- `{param_name}` ({param_def.get('type', 'unknown')}): {param_def.get('description', 'No description')}\n"
            
            doc += "\n"
        
        return doc
    
    def _error_response(self, message: str) -> Dict[str, Any]:
        """Create an error response."""
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -1,
                "message": message
            }
        }
    
    async def run(self):
        """Run the MCP server."""
        logger.info("Starting SMC Housing MCP Server", version=settings.server_version)
        
        try:
            # Read from stdin and write to stdout for MCP protocol
            while True:
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                try:
                    request = json.loads(line.strip())
                    response = await self.handle_request(request)
                    print(json.dumps(response))
                    sys.stdout.flush()
                except json.JSONDecodeError:
                    logger.warning("Invalid JSON received", line=line.strip())
                except Exception as e:
                    logger.error("Error processing request", error=str(e))
                    
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error("Server error", error=str(e))
        finally:
            await self._cleanup()
    
    async def _cleanup(self):
        """Clean up resources."""
        logger.info("Cleaning up resources")
        try:
            # Clean up extractors
            income_limits_extractor.cleanup()
            
            # Clean up cache if needed
            # await cache_manager.clear()
            
        except Exception as e:
            logger.warning("Cleanup error", error=str(e))


async def main():
    """Main entry point."""
    server = SMCHousingMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())

