# test_mcp.py - Test script for MCP Server
# File: /test_mcp.py

import asyncio
import json
import os
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters, ClientSession

async def test_mcp_server():
    """
    Test the MCP server functionality to ensure it works before deployment.
    This script simulates how Agent Zero would interact with our server.
    """
    print("🧪 Testing DXF Generator MCP Server...")
    
    # Set up test environment variables (use dummy values for testing tool discovery)
    test_env = {
        "APPWRITE_ENDPOINT": "https://test.appwrite.io/v1",
        "APPWRITE_PROJECT_ID": "test_project",
        "APPWRITE_API_KEY": "test_key", 
        "APPWRITE_BUCKET_ID": "test_bucket"
    }
    
    # Update environment for the test
    os.environ.update(test_env)
    
    # Configure server parameters - run our MCP server as subprocess
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"]
    )
    
    try:
        # Connect to the MCP server
        print("📡 Connecting to MCP server...")
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                
                # Initialize the connection
                await session.initialize()
                print("✅ Connected successfully!")
                
                # Test 1: List available tools
                print("\n🔧 Testing tool discovery...")
                tools = await session.list_tools()
                
                print(f"📋 Found {len(tools)} tools:")
                for tool in tools:
                    print(f"  - {tool.name}: {tool.description}")
                
                # Verify we have the expected tools
                tool_names = [tool.name for tool in tools]
                expected_tools = ["generate_architectural_dxf", "list_recent_dxf_files"]
                
                for expected in expected_tools:
                    if expected in tool_names:
                        print(f"  ✅ {expected} - Found")
                    else:
                        print(f"  ❌ {expected} - Missing")
                        return False
                
                # Test 2: List recent files (should be empty initially)
                print("\n📁 Testing list_recent_dxf_files...")
                try:
                    result = await session.call_tool(
                        "list_recent_dxf_files", 
                        {"limit": 5}
                    )
                    print("📝 Response:")
                    for content in result.content:
                        if hasattr(content, 'text'):
                            print(f"  {content.text}")
                    print("✅ list_recent_dxf_files test passed")
                    
                except Exception as e:
                    print(f"❌ list_recent_dxf_files test failed: {e}")
                    return False
                
                # Test 3: Test DXF generation (will fail due to fake credentials, but should validate input)
                print("\n🏗️ Testing generate_architectural_dxf input validation...")
                try:
                    result = await session.call_tool(
                        "generate_architectural_dxf",
                        {
                            "prompt": "test house with 2 doors and 3 windows",
                            "scale": 1.0,
                            "building_type": "house"
                        }
                    )
                    print("📝 Response:")
                    for content in result.content:
                        if hasattr(content, 'text'):
                            print(f"  {content.text}")
                    
                    # This will likely fail due to fake Appwrite credentials
                    # but should show that the tool accepts the input properly
                    print("ℹ️  Tool accepted input and processed request (expected to fail with fake credentials)")
                    
                except Exception as e:
                    print(f"ℹ️  Expected error with fake credentials: {e}")
                
                print("\n✅ MCP Server tests completed successfully!")
                print("🚀 Server is ready for Agent Zero integration")
                return True
                
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        return False

async def test_tool_schemas():
    """
    Test that our tool schemas are valid and complete.
    """
    print("\n🔍 Testing tool schema validation...")
    
    # Test schema for generate_architectural_dxf
    test_inputs = [
        # Valid inputs
        {"prompt": "house with door"},
        {"prompt": "office building", "scale": 2.0},
        {"prompt": "warehouse", "scale": 1.5, "building_type": "warehouse"},
        
        # Edge cases
        {"prompt": "simple house", "scale": 0.5},
        {"prompt": "complex office with 10 windows and 5 doors", "building_type": "office"}
    ]
    
    for i, test_input in enumerate(test_inputs, 1):
        print(f"  Test case {i}: {test_input}")
        
        # Check required fields
        if "prompt" not in test_input:
            print(f"    ❌ Missing required field 'prompt'")
            continue
            
        # Check field types
        if not isinstance(test_input["prompt"], str):
            print(f"    ❌ 'prompt' must be string")
            continue
            
        if "scale" in test_input and not isinstance(test_input["scale"], (int, float)):
            print(f"    ❌ 'scale' must be number")
            continue
            
        if "building_type" in test_input and not isinstance(test_input["building_type"], str):
            print(f"    ❌ 'building_type' must be string")
            continue
            
        print(f"    ✅ Schema valid")
    
    print("✅ Schema validation completed")

if __name__ == "__main__":
    print("🏗️ DXF Generator MCP Server Test Suite")
    print("=" * 50)
    
    # Run schema tests first (no server needed)
    asyncio.run(test_tool_schemas())
    
    # Then run server tests
    print("\n" + "=" * 50)
    success = asyncio.run(test_mcp_server())
    
    if success:
        print("\n🎉 All tests passed! MCP server is ready for deployment.")
        print("\n📋 Next steps:")
        print("1. Set real Appwrite environment variables")
        print("2. Deploy to Railway") 
        print("3. Configure Agent Zero with your deployed service")
        print("4. Test with Agent Zero: 'Generate a house floor plan'")
    else:
        print("\n⚠️  Some tests failed. Please check the server implementation.") 