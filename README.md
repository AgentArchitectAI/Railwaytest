# DXF Generator Service

**File: /README.md**

A service that generates architectural DXF (CAD) drawings from text descriptions. Now supports both traditional HTTP API and Model Context Protocol (MCP) for Agent Zero integration.

## 🏗️ What This Service Does

- **Generates DXF files** from natural language descriptions
- **Creates architectural floor plans** with doors, windows, rooms, and dimensions
- **Supports different building types** (house, office, warehouse, etc.)
- **Uploads files to Appwrite storage** and provides download URLs
- **Works with Agent Zero** via MCP protocol for AI agent integration

## 🚀 Quick Start

### Using with Agent Zero (MCP)

1. **Deploy to Railway:**
   ```bash
   # Set environment variables in Railway:
   APPWRITE_ENDPOINT=your_endpoint
   APPWRITE_PROJECT_ID=your_project_id
   APPWRITE_API_KEY=your_api_key
   APPWRITE_BUCKET_ID=your_bucket_id
   ```

2. **Configure Agent Zero:**
   ```yaml
   # Add to your Agent Zero config
   mcp:
     servers:
       dxf_generator:
         command: "python"
         args: ["mcp_server.py"]
         env:
           APPWRITE_ENDPOINT: "${APPWRITE_ENDPOINT}"
           APPWRITE_PROJECT_ID: "${APPWRITE_PROJECT_ID}"
           APPWRITE_API_KEY: "${APPWRITE_API_KEY}"
           APPWRITE_BUCKET_ID: "${APPWRITE_BUCKET_ID}"
   ```

3. **Use with Agent Zero:**
   ```
   Agent: "Generate a floor plan for a small house with 2 doors and 3 windows"
   ```

### Traditional HTTP API

Send POST requests to the root endpoint:

```bash
curl -X POST http://your-service-url/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "house with 2 doors and 3 windows"}'
```

## 🛠️ Available Tools (MCP)

### `generate_architectural_dxf`
Creates DXF architectural plans from text descriptions.

**Parameters:**
- `prompt` (required): Description of the architectural plan
- `scale` (optional): Scale factor (default: 1.0)  
- `building_type` (optional): Type of building (house/office/warehouse)

**Example:**
```json
{
  "prompt": "office building with 4 doors and 6 windows",
  "scale": 1.5,
  "building_type": "office"
}
```

### `list_recent_dxf_files`
Lists recently generated DXF files from the current session.

**Parameters:**
- `limit` (optional): Maximum number of files to return (default: 10)

## 🏗️ Architecture Features

The service intelligently analyzes your text prompt to include:

### **Automatic Feature Detection**
- **Doors**: Detects "2 doors", "door", etc. and places them strategically
- **Windows**: Recognizes "3 windows", "window", etc. and distributes them on walls
- **Rooms**: Identifies "bedroom", "kitchen", "bathroom" and adds interior walls
- **Building Types**: Adjusts dimensions based on house/office/warehouse

### **Smart Building Sizing**
- **House**: 8m x 6m base dimensions
- **Office**: 12m x 8m base dimensions  
- **Warehouse**: 20m x 15m base dimensions
- **Custom**: Scales all dimensions by your scale factor

### **Professional DXF Output**
- **Organized Layers**: WALLS, DOORS, WINDOWS, TEXT, DIMENSIONS
- **Proper Colors**: Different colors for each element type
- **Dimensions**: Automatic width/height measurements
- **Room Labels**: Interior space identification
- **Door Swings**: Architectural door swing arcs

## 📁 File Structure

```
├── main.py              # Original HTTP service (backward compatibility)
├── mcp_server.py        # New MCP server for Agent Zero
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container setup
├── railway.json        # Railway deployment config
├── agent_zero_config.yaml  # Agent Zero configuration example
└── README.md           # This file
```

## 🔧 Environment Variables

Required for Appwrite storage:

```bash
APPWRITE_ENDPOINT=https://your-appwrite-instance.com/v1
APPWRITE_PROJECT_ID=your_project_id
APPWRITE_API_KEY=your_api_key
APPWRITE_BUCKET_ID=your_bucket_id
```

## 🐳 Deployment

### Railway (Recommended)
1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on push

### Docker
```bash
# Build image
docker build -t dxf-generator .

# Run MCP server (default)
docker run -e APPWRITE_ENDPOINT=... dxf-generator

# Run HTTP server
docker run -e APPWRITE_ENDPOINT=... dxf-generator python main.py
```

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run MCP server
python mcp_server.py

# Run HTTP server  
python main.py
```

## 🔗 Integration Examples

### Agent Zero Usage

Once configured, Agent Zero can use natural language to generate CAD files:

```
User: "I need a floor plan for a small office with a reception area"

Agent: I'll generate an office floor plan for you with a reception area.

[Uses generate_architectural_dxf tool]

Agent: ✅ I've created an office floor plan DXF file for you!
📝 Description: Small office with reception area
📏 Scale: 1.0  
🏢 Building type: office
🔗 Download: [URL]

The DXF file includes:
- 12m x 8m office space (appropriate for commercial use)
- Reception area layout with interior walls
- Professional door and window placement
- Proper architectural layers and dimensions

You can open this file in AutoCAD, FreeCAD, or any CAD software.
```

### Programmatic HTTP Usage

```python
import requests
import json

response = requests.post('http://your-service//', 
    headers={'Content-Type': 'application/json'},
    data=json.dumps({
        'prompt': 'warehouse with loading dock and 2 offices'
    }),
    stream=True
)

for line in response.iter_lines():
    if line.startswith(b'data:'):
        data = json.loads(line[5:])
        print(data.get('text', ''))
        if 'url' in data:
            print(f"Download: {data['url']}")
```

## 🎯 Use Cases

- **Architects**: Quick concept sketches and initial layouts
- **Real Estate**: Property layout visualization  
- **Contractors**: Basic floor plan references
- **AI Agents**: Automated CAD generation from natural language
- **Developers**: Integration into larger design workflows

## 🔄 Backward Compatibility

The original HTTP API remains fully functional. Both interfaces can run simultaneously:

- **MCP Mode**: `python mcp_server.py` (default in Docker)
- **HTTP Mode**: `python main.py`

## 📝 Notes

- DXF files are industry-standard CAD format
- Files are temporarily stored locally, then uploaded to Appwrite
- All temporary files are automatically cleaned up
- Session memory tracks recent files (max 20)
- Supports multiple concurrent users via separate sessions

## 🔒 Security

- Environment variables for sensitive credentials
- Read-only file access for public downloads
- Automatic cleanup of temporary files
- Validated input parameters
- Error handling prevents system exposure

---

**Ready to create architectural drawings with AI? Deploy this service and start generating CAD files from natural language!** 🏗️✨ 