#!/usr/bin/env python3
"""Advanced test script for the SMC Housing MCP Server."""

import asyncio
import json
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import SMCHousingMCPServer


async def test_advanced_functionality():
    """Test advanced server functionality."""
    print("Testing Advanced SMC Housing MCP Server Functionality...")
    
    server = SMCHousingMCPServer()
    
    # Test income limits tool
    print("\n1. Testing income limits tool...")
    income_limits_request = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "get_income_limits",
            "arguments": {
                "year": 2025,
                "family_size": 3,
                "use_cache": False
            }
        }
    }
    
    response = await server.handle_request(income_limits_request)
    print(f"Income limits response: {json.dumps(response, indent=2)}")
    
    # Test eligibility check
    print("\n2. Testing eligibility check...")
    eligibility_request = {
        "jsonrpc": "2.0",
        "id": 6,
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
    
    response = await server.handle_request(eligibility_request)
    print(f"Eligibility check response: {json.dumps(response, indent=2)}")
    
    # Test public notices
    print("\n3. Testing public notices...")
    notices_request = {
        "jsonrpc": "2.0",
        "id": 7,
        "method": "tools/call",
        "params": {
            "name": "get_public_notices",
            "arguments": {
                "limit": 5,
                "use_cache": False
            }
        }
    }
    
    response = await server.handle_request(notices_request)
    print(f"Public notices response: {json.dumps(response, indent=2)}")
    
    # Test search functionality
    print("\n4. Testing search functionality...")
    search_request = {
        "jsonrpc": "2.0",
        "id": 8,
        "method": "tools/call",
        "params": {
            "name": "search_housing_data",
            "arguments": {
                "query": "affordable housing",
                "data_type": "all",
                "limit": 3
            }
        }
    }
    
    response = await server.handle_request(search_request)
    print(f"Search response: {json.dumps(response, indent=2)}")
    
    # Test resource reading
    print("\n5. Testing resource reading...")
    resource_request = {
        "jsonrpc": "2.0",
        "id": 9,
        "method": "resources/read",
        "params": {
            "uri": "smcgov://housing/housing_context"
        }
    }
    
    response = await server.handle_request(resource_request)
    print(f"Resource read response: {json.dumps(response, indent=2)}")
    
    print("\n✅ Advanced functionality tests completed successfully!")
    
    # Cleanup
    await server._cleanup()


async def test_error_handling():
    """Test error handling."""
    print("\n\nTesting Error Handling...")
    
    server = SMCHousingMCPServer()
    
    # Test unknown method
    print("\n1. Testing unknown method...")
    unknown_request = {
        "jsonrpc": "2.0",
        "id": 10,
        "method": "unknown/method"
    }
    
    response = await server.handle_request(unknown_request)
    print(f"Unknown method response: {json.dumps(response, indent=2)}")
    
    # Test unknown tool
    print("\n2. Testing unknown tool...")
    unknown_tool_request = {
        "jsonrpc": "2.0",
        "id": 11,
        "method": "tools/call",
        "params": {
            "name": "unknown_tool",
            "arguments": {}
        }
    }
    
    response = await server.handle_request(unknown_tool_request)
    print(f"Unknown tool response: {json.dumps(response, indent=2)}")
    
    # Test invalid arguments
    print("\n3. Testing invalid arguments...")
    invalid_args_request = {
        "jsonrpc": "2.0",
        "id": 12,
        "method": "tools/call",
        "params": {
            "name": "check_eligibility",
            "arguments": {
                "annual_income": "invalid",
                "family_size": 3
            }
        }
    }
    
    response = await server.handle_request(invalid_args_request)
    print(f"Invalid arguments response: {json.dumps(response, indent=2)}")
    
    print("\n✅ Error handling tests completed!")


if __name__ == "__main__":
    print("SMC Housing MCP Server Advanced Test Suite")
    print("=" * 60)
    
    try:
        asyncio.run(test_advanced_functionality())
        asyncio.run(test_error_handling())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()

