#!/usr/bin/env python3
"""Simple MCP client demonstration for the SMC Housing MCP Server."""

import asyncio
import json
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import SMCHousingMCPServer


async def demonstrate_mcp_usage():
    """Demonstrate how to use the MCP server."""
    print("SMC Housing MCP Server Demonstration")
    print("=" * 50)
    
    server = SMCHousingMCPServer()
    
    # 1. Initialize the server
    print("\n1. Initializing MCP Server...")
    init_response = await server.handle_request({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "demo-client", "version": "1.0.0"}
        }
    })
    print("✅ Server initialized successfully")
    
    # 2. List available tools
    print("\n2. Listing available tools...")
    tools_response = await server.handle_request({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list"
    })
    
    tools = tools_response["result"]["tools"]
    print(f"✅ Found {len(tools)} available tools:")
    for tool in tools:
        print(f"   - {tool['name']}: {tool['description']}")
    
    # 3. Test cache stats (no network required)
    print("\n3. Getting cache statistics...")
    cache_response = await server.handle_request({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "get_cache_stats",
            "arguments": {}
        }
    })
    
    cache_data = json.loads(cache_response["result"]["content"][0]["text"])
    print(f"✅ Cache stats: {cache_data}")
    
    # 4. Test eligibility check with mock data
    print("\n4. Testing eligibility check...")
    eligibility_response = await server.handle_request({
        "jsonrpc": "2.0",
        "id": 4,
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
    })
    
    eligibility_data = json.loads(eligibility_response["result"]["content"][0]["text"])
    print(f"✅ Eligibility check result:")
    print(f"   - Eligible: {eligibility_data['eligible']}")
    print(f"   - Income: ${eligibility_data['annual_income']:,}")
    print(f"   - Limit: ${eligibility_data['income_limit']:,}")
    print(f"   - Reason: {eligibility_data['reason']}")
    
    # 5. Test resource reading
    print("\n5. Reading housing context resource...")
    resource_response = await server.handle_request({
        "jsonrpc": "2.0",
        "id": 5,
        "method": "resources/read",
        "params": {
            "uri": "smcgov://housing/housing_context"
        }
    })
    
    context_text = resource_response["result"]["contents"][0]["text"]
    print(f"✅ Housing context loaded ({len(context_text)} characters)")
    print(f"   Preview: {context_text[:200]}...")
    
    # 6. Test error handling
    print("\n6. Testing error handling...")
    error_response = await server.handle_request({
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {
            "name": "nonexistent_tool",
            "arguments": {}
        }
    })
    
    if "error" in error_response:
        print(f"✅ Error handling works: {error_response['error']['message']}")
    
    print("\n" + "=" * 50)
    print("🎉 MCP Server demonstration completed successfully!")
    print("\nThe server is ready to be used with MCP clients.")
    print("It provides access to San Mateo County housing data through:")
    print("- Housing statistics and dashboard data")
    print("- Income limits and eligibility checking")
    print("- Public notices and announcements")
    print("- Search functionality across all data sources")
    
    # Cleanup
    await server._cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(demonstrate_mcp_usage())
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()

