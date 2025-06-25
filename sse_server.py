"""SSE wrapper for San Mateo County Housing MCP Server."""

import asyncio
import json
import uuid
from datetime import datetime
from typing import AsyncGenerator, Dict, Any
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import structlog

# Import our MCP server
from server import SMCHousingMCPServer

logger = structlog.get_logger()

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

# Global MCP server instance
mcp_server = SMCHousingMCPServer()

class SSEFormatter:
    """Format messages for Server-Sent Events."""
    
    @staticmethod
    def format_event(event_type: str, data: Any, event_id: str = None) -> str:
        """Format data as SSE event."""
        lines = []
        
        if event_id:
            lines.append(f"id: {event_id}")
        
        lines.append(f"event: {event_type}")
        
        if isinstance(data, (dict, list)):
            data = json.dumps(data, default=str)
        
        # Split data into multiple lines if needed
        for line in str(data).split('\n'):
            lines.append(f"data: {line}")
        
        lines.append("")  # Empty line to end event
        return "\n".join(lines) + "\n"

async def sse_generator(request: Request) -> AsyncGenerator[str, None]:
    """Generate SSE events for MCP communication."""
    try:
        # Send initial connection event
        yield SSEFormatter.format_event("connected", {
            "message": "Connected to SMC Housing MCP Server",
            "timestamp": datetime.now().isoformat(),
            "server_info": mcp_server.server_info
        })
        
        # Send server capabilities
        capabilities_response = await mcp_server._handle_initialize({})
        yield SSEFormatter.format_event("capabilities", capabilities_response)
        
        # Send available tools
        tools_response = await mcp_server._handle_tools_list()
        yield SSEFormatter.format_event("tools", tools_response)
        
        # Send available resources
        resources_response = await mcp_server._handle_resources_list()
        yield SSEFormatter.format_event("resources", resources_response)
        
        # Keep connection alive and listen for disconnect
        while True:
            if await request.is_disconnected():
                logger.info("Client disconnected")
                break
            
            # Send keepalive every 30 seconds
            yield SSEFormatter.format_event("keepalive", {
                "timestamp": datetime.now().isoformat()
            })
            
            await asyncio.sleep(30)
            
    except Exception as e:
        logger.error("SSE generator error", error=str(e))
        yield SSEFormatter.format_event("error", {
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
        "endpoints": {
            "/sse": "Server-Sent Events endpoint for MCP communication",
            "/tools": "Get available MCP tools",
            "/resources": "Get available MCP resources",
            "/call/{tool_name}": "Call a specific MCP tool"
        },
        "server_info": mcp_server.server_info
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

@app.get("/tools")
async def get_tools():
    """Get available MCP tools."""
    return await mcp_server._handle_tools_list()

@app.get("/resources")
async def get_resources():
    """Get available MCP resources."""
    return await mcp_server._handle_resources_list()

@app.post("/call/{tool_name}")
async def call_tool(tool_name: str, request: Request):
    """Call a specific MCP tool."""
    try:
        body = await request.json()
        arguments = body.get("arguments", {})
        
        mcp_request = {
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        response = await mcp_server.handle_request(mcp_request)
        return response
        
    except Exception as e:
        logger.error("Tool call error", tool=tool_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """General MCP endpoint for JSON-RPC requests."""
    try:
        body = await request.json()
        response = await mcp_server.handle_request(body)
        return response
        
    except Exception as e:
        logger.error("MCP request error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "server_info": mcp_server.server_info
    }

if __name__ == "__main__":
    import uvicorn
    import os
    
    logger.info("Starting SMC Housing MCP SSE Server")
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )