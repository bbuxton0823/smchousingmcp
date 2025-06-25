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
        "description": "Get current housing statistics and metrics",
        "inputSchema": {
            "type": "object",
            "properties": {
                "use_cache": {"type": "boolean", "default": True}
            }
        }
    },
    {
        "name": "get_income_limits",
        "description": "Get income limits by year and family size",
        "inputSchema": {
            "type": "object",
            "properties": {
                "year": {"type": "integer", "minimum": 2023, "maximum": 2025},
                "family_size": {"type": "integer", "minimum": 1, "maximum": 8}
            }
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
        # Send initial connection event
        yield format_sse_event("connected", {
            "message": "Connected to SMC Housing MCP Server",
            "timestamp": datetime.now().isoformat(),
            "server_info": SERVER_INFO
        })
        
        # Send capabilities
        yield format_sse_event("capabilities", {
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}, "resources": {}},
                "serverInfo": SERVER_INFO
            }
        })
        
        # Send tools
        yield format_sse_event("tools", {
            "result": {"tools": MOCK_TOOLS}
        })
        
        # Keep connection alive
        while True:
            if await request.is_disconnected():
                break
            
            yield format_sse_event("keepalive", {
                "timestamp": datetime.now().isoformat()
            })
            
            await asyncio.sleep(30)
            
    except Exception as e:
        yield format_sse_event("error", {
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        })

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

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)