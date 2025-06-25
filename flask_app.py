"""
Standalone MCP Server for San Mateo County Housing Data
Fixed version that properly implements MCP protocol over HTTP
"""

import asyncio
import json
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

# Create Flask app
app = Flask(__name__)
CORS(app)

class FixedSMCHousingMCPServer:
    """Fixed San Mateo County Housing MCP Server with proper HTTP support."""
    
    def __init__(self):
        self.server_info = {
            "name": "SMC Housing MCP Server",
            "version": "1.0.0",
            "description": "San Mateo County Housing MCP Server with proper HTTP support"
        }
        
        # Define available tools with proper MCP format
        self.tools = [
            {
                "name": "get_housing_statistics",
                "description": "Get current housing statistics and metrics from San Mateo County",
                "inputSchema": {
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
            {
                "name": "get_income_limits",
                "description": "Get income limits by year and family size for San Mateo County housing programs",
                "inputSchema": {
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
                            "description": "Number of people in family",
                            "minimum": 1,
                            "maximum": 8
                        }
                    }
                }
            },
            {
                "name": "search_housing_data",
                "description": "Search across all San Mateo County housing data sources",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "data_type": {
                            "type": "string",
                            "description": "Type of data to search",
                            "enum": ["all", "statistics", "income_limits", "notices"],
                            "default": "all"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "check_eligibility",
                "description": "Check eligibility for San Mateo County housing programs based on income",
                "inputSchema": {
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
                        }
                    },
                    "required": ["annual_income", "family_size"]
                }
            }
        ]
        
        # Define available resources
        self.resources = [
            {
                "uri": "smcgov://housing/context",
                "name": "housing_context",
                "description": "Comprehensive context about San Mateo County housing programs",
                "mimeType": "text/plain"
            },
            {
                "uri": "smcgov://housing/docs",
                "name": "api_documentation", 
                "description": "Documentation for available MCP tools and resources",
                "mimeType": "text/markdown"
            }
        ]
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests with proper JSON-RPC format."""
        try:
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            if method == "initialize":
                return self._handle_initialize(params, request_id)
            elif method == "tools/list":
                return self._handle_tools_list(request_id)
            elif method == "tools/call":
                return self._handle_tool_call(params, request_id)
            elif method == "resources/list":
                return self._handle_resources_list(request_id)
            elif method == "resources/read":
                return self._handle_resource_read(params, request_id)
            else:
                return self._error_response(f"Unknown method: {method}", request_id)
                
        except Exception as e:
            return self._error_response(str(e), request.get("id"))
    
    def _handle_initialize(self, params: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
        """Handle initialization request."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {}
                },
                "serverInfo": self.server_info
            }
        }
    
    def _handle_tools_list(self, request_id: Any) -> Dict[str, Any]:
        """Handle tools list request."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": self.tools
            }
        }
    
    def _handle_tool_call(self, params: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
        """Handle tool call request."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not tool_name:
            return self._error_response("Missing tool name", request_id)
        
        # Check if tool exists
        tool_names = [tool["name"] for tool in self.tools]
        if tool_name not in tool_names:
            return self._error_response(f"Unknown tool: {tool_name}", request_id)
        
        try:
            result = self._execute_tool(tool_name, arguments)
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
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
            return self._error_response(f"Tool execution failed: {str(e)}", request_id)
    
    def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a specific tool with mock data."""
        if tool_name == "get_housing_statistics":
            return {
                "total_units": 4939,
                "active_projects": 68,
                "county_funding": 305300000,
                "federal_funding": 52600000,
                "units_by_status": {
                    "complete": 2875,
                    "predevelopment": 1202,
                    "construction": 862
                },
                "last_updated": datetime.now().isoformat()
            }
        
        elif tool_name == "get_income_limits":
            year = arguments.get("year", 2025)
            family_size = arguments.get("family_size", 1)
            
            # Mock income limits data
            base_limits = {
                1: {"30%": 31200, "50%": 52000, "80%": 83200, "120%": 124800},
                2: {"30%": 35650, "50%": 59400, "80%": 95050, "120%": 142600},
                3: {"30%": 40100, "50%": 66850, "80%": 106950, "120%": 160400},
                4: {"30%": 44550, "50%": 74250, "80%": 118800, "120%": 178200}
            }
            
            limits = base_limits.get(family_size, base_limits[1])
            
            return {
                "year": year,
                "family_size": family_size,
                "income_limits": limits,
                "area": "San Mateo County",
                "last_updated": datetime.now().isoformat()
            }
        
        elif tool_name == "search_housing_data":
            query = arguments.get("query", "")
            data_type = arguments.get("data_type", "all")
            
            return {
                "query": query,
                "data_type": data_type,
                "results": [
                    {
                        "type": "statistics",
                        "title": "Housing Statistics",
                        "description": f"Found housing data related to: {query}",
                        "relevance": "high"
                    }
                ],
                "total_results": 1
            }
        
        elif tool_name == "check_eligibility":
            annual_income = arguments.get("annual_income", 0)
            family_size = arguments.get("family_size", 1)
            
            # Simple eligibility calculation
            ami_80_limit = {1: 83200, 2: 95050, 3: 106950, 4: 118800}.get(family_size, 83200)
            
            eligible = annual_income <= ami_80_limit
            max_rent = annual_income * 0.3 / 12  # 30% of income
            
            return {
                "eligible": eligible,
                "annual_income": annual_income,
                "family_size": family_size,
                "ami_80_limit": ami_80_limit,
                "max_affordable_rent": round(max_rent, 2),
                "eligibility_category": "80% AMI" if eligible else "Above 80% AMI"
            }
        
        else:
            raise ValueError(f"Tool not implemented: {tool_name}")
    
    def _handle_resources_list(self, request_id: Any) -> Dict[str, Any]:
        """Handle resources list request."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "resources": self.resources
            }
        }
    
    def _handle_resource_read(self, params: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
        """Handle resource read request."""
        uri = params.get("uri", "")
        
        if uri == "smcgov://housing/context":
            content = self._get_housing_context()
        elif uri == "smcgov://housing/docs":
            content = self._get_api_documentation()
        else:
            return self._error_response(f"Unknown resource: {uri}", request_id)
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
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
    
    def _get_housing_context(self) -> str:
        """Get comprehensive housing context."""
        return f"""
San Mateo County Department of Housing - Data Context

The San Mateo County Department of Housing provides various programs and services
to address housing needs in the county. This MCP server provides access to:

1. Housing Statistics:
   - Total affordable housing units: 4,939
   - Active projects: 68
   - County funding: $305.3M
   - Federal funding: $52.6M

2. Income Limits:
   - Area Median Income (AMI) categories: 30%, 50%, 80%, 120%
   - Family sizes: 1-8 people
   - Updated annually

3. Eligibility Checking:
   - Income-based eligibility for housing programs
   - Rent affordability calculations

Server: {self.server_info['name']} v{self.server_info['version']}
Last updated: {datetime.now().isoformat()}
        """.strip()
    
    def _get_api_documentation(self) -> str:
        """Get API documentation."""
        doc = "# San Mateo County Housing MCP Server API\n\n"
        doc += "## Available Tools\n\n"
        
        for tool in self.tools:
            doc += f"### {tool['name']}\n"
            doc += f"{tool['description']}\n\n"
            
            properties = tool['inputSchema'].get('properties', {})
            if properties:
                doc += "**Parameters:**\n"
                for param_name, param_def in properties.items():
                    doc += f"- `{param_name}` ({param_def.get('type', 'unknown')}): {param_def.get('description', 'No description')}\n"
            doc += "\n"
        
        return doc
    
    def _error_response(self, message: str, request_id: Any = None) -> Dict[str, Any]:
        """Create an error response."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": message
            }
        }

# Create server instance
mcp_server = FixedSMCHousingMCPServer()

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with server information."""
    return jsonify({
        "name": "SMC Housing MCP Server",
        "version": "1.0.0",
        "description": "San Mateo County Housing MCP Server - Fixed Version",
        "status": "healthy",
        "protocol": "MCP over HTTP (JSON-RPC 2.0)",
        "endpoints": {
            "/mcp": "Main MCP JSON-RPC endpoint (POST)",
            "/health": "Health check endpoint (GET)",
            "/tools": "Debug: List available tools (GET)",
            "/initialize": "MCP initialize endpoint (POST)",
            "/tools/call": "MCP tool call endpoint (POST)",
            "/resources/list": "MCP resources list endpoint (GET/POST)",
            "/resources/read": "MCP resources read endpoint (POST)"
        },
        "server_info": mcp_server.server_info
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "server_info": mcp_server.server_info,
        "version": "1.0.0"
    })

@app.route('/mcp', methods=['POST'])
def mcp_endpoint():
    """Main MCP JSON-RPC endpoint."""
    try:
        if not request.is_json:
            return jsonify({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32700,
                    "message": "Parse error - Content-Type must be application/json"
                }
            }), 400
        
        mcp_request = request.get_json()
        
        if not isinstance(mcp_request, dict) or "method" not in mcp_request:
            return jsonify({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32600,
                    "message": "Invalid Request - Missing method field"
                }
            }), 400
        
        response = mcp_server.handle_request(mcp_request)
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }), 500

@app.route('/tools', methods=['GET'])
def tools_endpoint():
    """Debug endpoint to list available tools (fixed version)."""
    try:
        tools_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 1
        }
        
        response = mcp_server.handle_request(tools_request)
        
        # Return the properly formatted response
        return jsonify(response)
            
    except Exception as e:
        return jsonify({
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": f"Failed to extract MCP server tools: {str(e)}"
            }
        }), 500

@app.route('/initialize', methods=['POST'])
def initialize_endpoint():
    """MCP initialize endpoint."""
    try:
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": request.get_json() or {},
            "id": 1
        }
        
        response = mcp_server.handle_request(init_request)
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }), 500

@app.route('/tools/call', methods=['POST'])
def tool_call_endpoint():
    """MCP tool call endpoint."""
    try:
        tool_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": request.get_json() or {},
            "id": 1
        }
        
        response = mcp_server.handle_request(tool_request)
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }), 500

@app.route('/resources/list', methods=['GET', 'POST'])
def resources_list_endpoint():
    """MCP resources list endpoint."""
    try:
        resources_request = {
            "jsonrpc": "2.0",
            "method": "resources/list",
            "params": {},
            "id": 1
        }
        
        response = mcp_server.handle_request(resources_request)
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }), 500

@app.route('/resources/read', methods=['POST'])
def resources_read_endpoint():
    """MCP resources read endpoint."""
    try:
        read_request = {
            "jsonrpc": "2.0",
            "method": "resources/read",
            "params": request.get_json() or {},
            "id": 1
        }
        
        response = mcp_server.handle_request(read_request)
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)