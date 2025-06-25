#!/usr/bin/env python3
"""Test script for the SMC Housing MCP Server."""

import asyncio
import json
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import SMCHousingMCPServer


async def test_server():
    """Test basic server functionality."""
    print("Testing SMC Housing MCP Server...")
    
    server = SMCHousingMCPServer()
    
    # Test initialization
    print("\n1. Testing initialization...")
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    response = await server.handle_request(init_request)
    print(f"Initialize response: {json.dumps(response, indent=2)}")
    
    # Test tools list
    print("\n2. Testing tools list...")
    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list"
    }
    
    response = await server.handle_request(tools_request)
    print(f"Tools list response: {json.dumps(response, indent=2)}")
    
    # Test resources list
    print("\n3. Testing resources list...")
    resources_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "resources/list"
    }
    
    response = await server.handle_request(resources_request)
    print(f"Resources list response: {json.dumps(response, indent=2)}")
    
    # Test a simple tool call (cache stats)
    print("\n4. Testing cache stats tool...")
    tool_request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "get_cache_stats",
            "arguments": {}
        }
    }
    
    response = await server.handle_request(tool_request)
    print(f"Cache stats response: {json.dumps(response, indent=2)}")
    
    print("\n✅ Basic server tests completed successfully!")
    
    # Cleanup
    await server._cleanup()


async def test_extractors():
    """Test individual extractors."""
    print("\n\nTesting individual extractors...")
    
    # Test cache manager
    print("\n1. Testing cache manager...")
    from processors.cache_manager import cache_manager
    
    # Test cache operations
    await cache_manager.set("test_key", {"test": "data"}, ttl_hours=1)
    cached_data = await cache_manager.get("test_key")
    print(f"Cache test: {cached_data}")
    
    stats = await cache_manager.get_cache_stats()
    print(f"Cache stats: {stats}")
    
    # Test dashboard extractor (without actual web scraping)
    print("\n2. Testing dashboard extractor...")
    from extractors.dashboard import dashboard_extractor
    
    # This will likely fail without actual web access, but we can test the structure
    try:
        stats = await dashboard_extractor.get_housing_statistics(use_cache=False)
        print(f"Dashboard stats: {stats}")
    except Exception as e:
        print(f"Dashboard extraction failed (expected): {e}")
    
    print("\n✅ Extractor tests completed!")


if __name__ == "__main__":
    print("SMC Housing MCP Server Test Suite")
    print("=" * 50)
    
    try:
        asyncio.run(test_server())
        asyncio.run(test_extractors())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()

