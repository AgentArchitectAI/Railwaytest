# mcp_server.py - MCP Server for DXF Generation Service
# File: /mcp_server.py
import asyncio
import tempfile
import os
import uuid
import ezdxf
from appwrite.client import Client
from appwrite.services.storage import Storage
from mcp import ClientSession, StdioServerParameters
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializeResult
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent

# Initialize the MCP server
app = Server("dxf-generator")

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    List available tools for Agent Zero to discover.
    This replaces the need for hardcoded API specs.
    """
    return [
        Tool(
            name="generate_architectural_dxf",
            description="Generate DXF architectural plans from text descriptions. Creates CAD drawings based on natural language input.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string", 
                        "description": "Description of the architectural plan to generate (e.g., 'house with 2 doors and 3 windows')"
                    },
                    "scale": {
                        "type": "number",
                        "description": "Optional scale factor for the drawing (default: 1.0)",
                        "default": 1.0
                    },
                    "building_type": {
                        "type": "string",
                        "description": "Type of building (house, office, warehouse, etc.)",
                        "default": "house"
                    }
                },
                "required": ["prompt"]
            }
        ),
        Tool(
            name="list_recent_dxf_files",
            description="List recently generated DXF files from this session",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of files to return",
                        "default": 10
                    }
                }
            }
        )
    ]

# Store recent files in memory for this session
recent_files = []

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    Handle tool calls from Agent Zero.
    This is where the actual DXF generation logic executes.
    """
    global recent_files
    
    if name == "generate_architectural_dxf":
        try:
            prompt = arguments["prompt"]
            scale = arguments.get("scale", 1.0)
            building_type = arguments.get("building_type", "house")
            
            # Generate DXF file with enhanced logic
            filename = prompt.replace(" ", "_").replace(",", "").replace(".", "")[:50] + ".dxf"
            doc = ezdxf.new()
            
            # Enhanced drawing function with scale and building type support
            draw_architectural_plan(doc, prompt, scale, building_type)
            
            # Save to temp file
            temp_path = os.path.join(tempfile.gettempdir(), filename)
            doc.saveas(temp_path)
            
            # Upload to Appwrite storage
            file_url = await upload_to_appwrite(temp_path, filename)
            
            # Store in recent files
            file_info = {
                "filename": filename,
                "prompt": prompt,
                "url": file_url,
                "scale": scale,
                "building_type": building_type
            }
            recent_files.insert(0, file_info)  # Add to beginning
            recent_files = recent_files[:20]  # Keep only last 20 files
            
            return [
                TextContent(
                    type="text",
                    text=f"✅ Successfully generated DXF file: {filename}\n"
                         f"📝 Based on prompt: {prompt}\n"
                         f"📏 Scale: {scale}\n"
                         f"🏢 Building type: {building_type}\n"
                         f"🔗 Download URL: {file_url}\n\n"
                         f"💡 The DXF file contains architectural elements based on your description and can be opened in any CAD software."
                )
            ]
            
        except Exception as e:
            return [
                TextContent(
                    type="text", 
                    text=f"❌ Error generating DXF: {str(e)}\n"
                         f"Please check your prompt and try again. Make sure all environment variables are properly configured."
                )
            ]
    
    elif name == "list_recent_dxf_files":
        try:
            limit = arguments.get("limit", 10)
            recent_subset = recent_files[:limit]
            
            if not recent_subset:
                return [
                    TextContent(
                        type="text",
                        text="📁 No DXF files have been generated in this session yet.\n"
                             "Use the 'generate_architectural_dxf' tool to create some!"
                    )
                ]
            
            file_list = "📁 Recent DXF Files:\n\n"
            for i, file_info in enumerate(recent_subset, 1):
                file_list += f"{i}. **{file_info['filename']}**\n"
                file_list += f"   📝 Prompt: {file_info['prompt']}\n"
                file_list += f"   📏 Scale: {file_info['scale']}\n"
                file_list += f"   🏢 Type: {file_info['building_type']}\n"
                file_list += f"   🔗 URL: {file_info['url']}\n\n"
            
            return [
                TextContent(
                    type="text",
                    text=file_list
                )
            ]
            
        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=f"❌ Error listing files: {str(e)}"
                )
            ]
    else:
        raise ValueError(f"Unknown tool: {name}")

def draw_architectural_plan(doc, prompt_text, scale=1.0, building_type="house"):
    """
    Enhanced drawing function with better architectural elements.
    Creates more sophisticated DXF drawings based on prompt analysis.
    """
    msp = doc.modelspace()
    
    # Define layers for better organization
    doc.layers.new("WALLS", dxfattribs={"color": 1})      # Red
    doc.layers.new("DOORS", dxfattribs={"color": 2})      # Yellow  
    doc.layers.new("WINDOWS", dxfattribs={"color": 3})    # Green
    doc.layers.new("TEXT", dxfattribs={"color": 4})       # Cyan
    doc.layers.new("DIMENSIONS", dxfattribs={"color": 5}) # Blue
    
    # Base dimensions with scale - adjust based on building type
    if building_type.lower() in ["house", "home", "residential"]:
        base_width = 8000 * scale   # 8 meters for house
        base_height = 6000 * scale  # 6 meters for house
    elif building_type.lower() in ["office", "commercial"]:
        base_width = 12000 * scale  # 12 meters for office
        base_height = 8000 * scale  # 8 meters for office
    elif building_type.lower() in ["warehouse", "industrial"]:
        base_width = 20000 * scale  # 20 meters for warehouse
        base_height = 15000 * scale # 15 meters for warehouse
    else:
        base_width = 6000 * scale   # Default
        base_height = 4000 * scale  # Default
    
    # Main building outline (outer walls)
    msp.add_lwpolyline([
        (0, 0), (base_width, 0), (base_width, base_height), (0, base_height), (0, 0)
    ], dxfattribs={"closed": True, "layer": "WALLS", "lineweight": 50})
    
    # Analyze prompt for specific features
    prompt_lower = prompt_text.lower()
    
    # Count doors and windows from prompt
    door_count = prompt_lower.count("door")
    if "doors" in prompt_lower:
        # Try to extract number before "doors"
        import re
        numbers = re.findall(r'(\d+)\s*doors?', prompt_lower)
        if numbers:
            door_count = max(door_count, int(numbers[0]))
    
    window_count = prompt_lower.count("window") 
    if "windows" in prompt_lower:
        # Try to extract number before "windows"
        numbers = re.findall(r'(\d+)\s*windows?', prompt_lower)
        if numbers:
            window_count = max(window_count, int(numbers[0]))
    
    # Add doors
    door_width = 800 * scale
    if door_count > 0:
        for i in range(min(door_count, 4)):  # Max 4 doors
            if i == 0:  # Front door
                door_x = base_width/2 - door_width/2
                msp.add_line((door_x, 0), (door_x + door_width, 0), 
                            dxfattribs={"layer": "DOORS", "lineweight": 30})
                # Add door swing arc
                msp.add_arc(center=(door_x, 0), radius=door_width, 
                           start_angle=0, end_angle=90,
                           dxfattribs={"layer": "DOORS"})
            elif i == 1:  # Back door
                door_x = base_width/4
                msp.add_line((door_x, base_height), (door_x + door_width, base_height),
                            dxfattribs={"layer": "DOORS", "lineweight": 30})
            elif i == 2:  # Side door left
                door_y = base_height/2 - door_width/2
                msp.add_line((0, door_y), (0, door_y + door_width),
                            dxfattribs={"layer": "DOORS", "lineweight": 30})
            elif i == 3:  # Side door right
                door_y = base_height/2 - door_width/2  
                msp.add_line((base_width, door_y), (base_width, door_y + door_width),
                            dxfattribs={"layer": "DOORS", "lineweight": 30})
    
    # Add windows
    window_width = 1200 * scale
    window_depth = 150 * scale
    if window_count > 0:
        for i in range(min(window_count, 8)):  # Max 8 windows
            if i < 4:  # Front and back walls
                wall_side = 0 if i < 2 else 1  # 0 = front, 1 = back
                wall_y = 0 if wall_side == 0 else base_height
                
                window_x = (base_width / 4) * (1 + (i % 2))
                
                # Window opening in wall
                msp.add_line((window_x, wall_y), (window_x + window_width, wall_y),
                            dxfattribs={"layer": "WINDOWS", "lineweight": 25})
                
                # Window frame representation
                if wall_side == 0:  # Front wall
                    msp.add_rectangle((window_x, wall_y), window_width, window_depth,
                                     dxfattribs={"layer": "WINDOWS"})
                else:  # Back wall
                    msp.add_rectangle((window_x, wall_y - window_depth), window_width, window_depth,
                                     dxfattribs={"layer": "WINDOWS"})
            else:  # Side walls
                wall_side = 0 if i < 6 else 1  # 0 = left, 1 = right
                wall_x = 0 if wall_side == 0 else base_width
                
                window_y = (base_height / 3) * (1 + ((i - 4) % 2))
                
                # Window opening in wall
                msp.add_line((wall_x, window_y), (wall_x, window_y + window_width),
                            dxfattribs={"layer": "WINDOWS", "lineweight": 25})
    
    # Add interior elements if mentioned
    if any(word in prompt_lower for word in ["room", "bedroom", "kitchen", "bathroom"]):
        # Add some interior walls
        interior_wall_x = base_width / 2
        msp.add_line((interior_wall_x, 0), (interior_wall_x, base_height * 0.6),
                     dxfattribs={"layer": "WALLS", "lineweight": 30})
        
        # Add room labels
        msp.add_text("Living Room", 
                    dxfattribs={'height': 200 * scale, 'layer': 'TEXT'}
                    ).set_pos((base_width * 0.25, base_height * 0.5), align='MIDDLE_CENTER')
        
        msp.add_text("Bedroom", 
                    dxfattribs={'height': 200 * scale, 'layer': 'TEXT'}
                    ).set_pos((base_width * 0.75, base_height * 0.5), align='MIDDLE_CENTER')
    
    # Add main title text
    text_height = 300 * scale
    msp.add_text(f"{building_type.title()}: {prompt_text}", 
                dxfattribs={'height': text_height, 'layer': 'TEXT'}
                ).set_pos((100 * scale, base_height + 500 * scale), align='LEFT')
    
    # Add dimensions
    dim_text_height = 150 * scale
    msp.add_text(f"Width: {base_width/1000:.1f}m", 
                dxfattribs={'height': dim_text_height, 'layer': 'DIMENSIONS'}
                ).set_pos((base_width/2, -400 * scale), align='MIDDLE_CENTER')
    
    msp.add_text(f"Height: {base_height/1000:.1f}m", 
                dxfattribs={'height': dim_text_height, 'layer': 'DIMENSIONS', 'rotation': 90}
                ).set_pos((-400 * scale, base_height/2), align='MIDDLE_CENTER')

async def upload_to_appwrite(temp_path, filename):
    """
    Upload file to Appwrite storage with enhanced error handling.
    """
    try:
        # Validate environment variables
        required_env_vars = [
            "APPWRITE_ENDPOINT", 
            "APPWRITE_PROJECT_ID", 
            "APPWRITE_API_KEY", 
            "APPWRITE_BUCKET_ID"
        ]
        
        missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # Initialize Appwrite client
        client = Client()
        client.set_endpoint(os.environ["APPWRITE_ENDPOINT"])
        client.set_project(os.environ["APPWRITE_PROJECT_ID"]) 
        client.set_key(os.environ["APPWRITE_API_KEY"])
        storage = Storage(client)
        
        # Generate unique file ID
        file_id = uuid.uuid4().hex
        
        # Upload file
        with open(temp_path, "rb") as file:
            result = storage.create_file(
                bucket_id=os.environ["APPWRITE_BUCKET_ID"],
                file_id=file_id,
                file=file,
                read=["*"],  # Public read access
                write=[]     # No write access for security
            )
        
        # Clean up temp file
        os.unlink(temp_path)
        
        # Construct and return download URL
        download_url = (
            f"{os.environ['APPWRITE_ENDPOINT'].rstrip('/')}"
            f"/storage/buckets/{os.environ['APPWRITE_BUCKET_ID']}"
            f"/files/{file_id}/download"
            f"?project={os.environ['APPWRITE_PROJECT_ID']}"
        )
        
        return download_url
        
    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise e

async def main():
    """
    Main function to run the MCP server using stdio transport.
    This enables Agent Zero to communicate with the server via stdin/stdout.
    """
    try:
        # Run the MCP server using stdio transport
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream, 
                write_stream,
                InitializeResult(
                    protocolVersion="2024-11-05",
                    capabilities=app.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )
    except Exception as e:
        print(f"Error starting MCP server: {e}", file=sys.stderr)
        raise

if __name__ == "__main__":
    import sys
    print("🚀 Starting DXF Generator MCP Server...", file=sys.stderr)
    print("📡 Ready to receive requests from Agent Zero", file=sys.stderr)
    asyncio.run(main()) 