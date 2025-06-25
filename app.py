"""Simplified SSE server for Railway deployment."""

import asyncio
import json
import os
from datetime import datetime
from typing import AsyncGenerator
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SMC Housing MCP Server",
    description="San Mateo County Housing MCP Server with SSE support",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock MCP server data
SERVER_INFO = {
    "name": "SMC Housing MCP Server",
    "version": "1.0.0",
    "description": "San Mateo County Housing MCP Server with SSE support"
}

MOCK_TOOLS = [
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

def format_sse_event(event_type: str, data: dict, event_id: str = None) -> str:
    """Format data as SSE event."""
    lines = []
    
    if event_id:
        lines.append(f"id: {event_id}")
    
    lines.append(f"event: {event_type}")
    
    data_str = json.dumps(data, default=str)
    for line in data_str.split('\n'):
        lines.append(f"data: {line}")
    
    lines.append("")
    return "\n".join(lines) + "\n"

async def sse_generator(request: Request) -> AsyncGenerator[str, None]:
    """Generate SSE events for MCP communication."""
    try:
        # Send server info first
        yield format_sse_event("server_info", SERVER_INFO)
        
        # Send capabilities
        capabilities = {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {}
            },
            "serverInfo": SERVER_INFO
        }
        yield format_sse_event("capabilities", capabilities)
        
        # Send tools
        yield format_sse_event("tools", {"tools": MOCK_TOOLS})
        
        # Send ready signal
        yield format_sse_event("ready", {"status": "ready", "timestamp": datetime.now().isoformat()})
        
        # Keep connection alive
        while True:
            if await request.is_disconnected():
                break
            
            await asyncio.sleep(30)
            yield format_sse_event("ping", {"timestamp": datetime.now().isoformat()})
            
    except Exception as e:
        yield format_sse_event("error", {"error": str(e), "timestamp": datetime.now().isoformat()})

@app.get("/")
async def root():
    """Root endpoint with server information."""
    return {
        "name": "SMC Housing MCP Server",
        "version": "1.0.0",
        "description": "San Mateo County Housing MCP Server with SSE support",
        "status": "healthy",
        "endpoints": {
            "/sse": "Server-Sent Events endpoint for MCP communication",
            "/health": "Health check endpoint",
            "/tools": "Get available MCP tools"
        },
        "server_info": SERVER_INFO
    }

@app.get("/sse")
async def sse_endpoint(request: Request):
    """SSE endpoint for MCP communication."""
    return StreamingResponse(
        sse_generator(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "server_info": SERVER_INFO,
        "version": "1.0.0"
    }

@app.get("/tools")
async def get_tools():
    """Get available MCP tools."""
    return {
        "result": {"tools": MOCK_TOOLS}
    }

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """Handle MCP JSON-RPC requests."""
    try:
        body = await request.json()
        method = body.get("method")
        request_id = body.get("id", 1)
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {}
                    },
                    "serverInfo": SERVER_INFO
                }
            }
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": MOCK_TOOLS
                }
            }
        elif method == "tools/call":
            tool_name = body.get("params", {}).get("name")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Mock response from {tool_name} tool"
                        }
                    ]
                }
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": str(e)
            }
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)