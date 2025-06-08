# Railway Deployment Guide

**File: /DEPLOYMENT.md**

Step-by-step guide to deploy your DXF Generator service to Railway and integrate with Agent Zero.

## 🚀 Quick Deploy to Railway

### Step 1: Prepare Your Repository

1. **Ensure all files are committed:**
   ```bash
   git add .
   git commit -m "Add MCP server support for Agent Zero"
   git push origin main
   ```

### Step 2: Deploy to Railway

1. **Connect to Railway:**
   - Go to [railway.app](https://railway.app)
   - Click "Start a New Project"
   - Choose "Deploy from GitHub repo"
   - Select your repository

2. **Configure Environment Variables:**
   In Railway dashboard, add these variables:
   ```
   APPWRITE_ENDPOINT=https://your-appwrite-instance.com/v1
   APPWRITE_PROJECT_ID=your_project_id
   APPWRITE_API_KEY=your_api_key_with_write_permissions
   APPWRITE_BUCKET_ID=your_bucket_id_for_files
   ```

3. **Deploy:**
   - Railway will automatically build and deploy
   - Default command runs MCP server: `python mcp_server.py`
   - For HTTP mode, override with: `python main.py`

### Step 3: Test Your Deployment

```bash
# Test HTTP endpoint (if running main.py)
curl -X POST https://your-app.railway.app/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test house with door"}'

# For MCP mode, it will be accessible via stdio only
```

## 🤖 Agent Zero Integration

### Step 1: Install Agent Zero

Follow the [Agent Zero installation guide](https://github.com/frdel/agent-zero) or use Docker:

```bash
# Clone Agent Zero
git clone https://github.com/frdel/agent-zero.git
cd agent-zero

# Set up environment
cp example.env .env
# Edit .env with your API keys (OpenAI, etc.)

# Run Agent Zero
python run_ui.py  # or run_cli.py
```

### Step 2: Configure MCP Server

Create or update your Agent Zero configuration file:

**`agent_config.yaml`:**
```yaml
mcp:
  servers:
    dxf_generator:
      # For Railway deployment, you'll need to run the server locally
      # or set up a tunnel. MCP typically uses stdio which works best locally.
      command: "python"
      args: ["path/to/your/mcp_server.py"]
      env:
        APPWRITE_ENDPOINT: "your_appwrite_endpoint"
        APPWRITE_PROJECT_ID: "your_project_id"
        APPWRITE_API_KEY: "your_api_key"
        APPWRITE_BUCKET_ID: "your_bucket_id"
      # Alternative: Clone your repo locally for MCP
      cwd: "/path/to/your/dxf-generator"
```

### Step 3: Local MCP Setup (Recommended)

Since MCP works best with stdio (local processes), we recommend running the DXF generator locally:

```bash
# Clone your repository to Agent Zero machine
git clone https://github.com/yourusername/your-dxf-repo.git
cd your-dxf-repo

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export APPWRITE_ENDPOINT="your_endpoint"
export APPWRITE_PROJECT_ID="your_project"
export APPWRITE_API_KEY="your_key"
export APPWRITE_BUCKET_ID="your_bucket"

# Test MCP server
python test_mcp.py
```

### Step 4: Configure Agent Zero

Update Agent Zero's configuration to use your MCP server:

**`prompts/default/agent.system.md`** (add to Agent Zero):
```markdown
You have access to architectural drawing tools via MCP:

- generate_architectural_dxf: Create CAD drawings from descriptions
- list_recent_dxf_files: List recently generated files

When users ask for floor plans, building designs, or CAD drawings:
1. Use generate_architectural_dxf tool
2. Explain what the DXF contains
3. Provide download links
4. Suggest CAD software to open files
```

## 🔧 Advanced Configuration

### Custom Agent Zero Integration

Create a custom tool wrapper in Agent Zero:

**`tools/dxf_generator.py`:**
```python
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters, ClientSession

class DXFGeneratorTool:
    def __init__(self):
        self.server_params = StdioServerParameters(
            command="python",
            args=["/path/to/your/mcp_server.py"]
        )
    
    async def generate_dxf(self, prompt, scale=1.0, building_type="house"):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                result = await session.call_tool(
                    "generate_architectural_dxf",
                    {
                        "prompt": prompt,
                        "scale": scale, 
                        "building_type": building_type
                    }
                )
                
                return result.content[0].text if result.content else "Error"
```

### Remote MCP via Cloudflare (Advanced)

For production deployments, consider using Cloudflare's MCP hosting:

1. **Deploy MCP Server to Cloudflare:**
   ```bash
   # Configure for Cloudflare Workers
   npm create cloudflare@latest your-mcp-server
   cd your-mcp-server
   
   # Copy your Python MCP server logic
   # Convert to JavaScript/TypeScript for Cloudflare
   ```

2. **Use HTTPS MCP Client:**
   ```yaml
   mcp:
     servers:
       dxf_generator:
         transport: "sse"
         url: "https://your-mcp-server.your-subdomain.workers.dev"
   ```

## 🧪 Testing Your Integration

### Test Workflow

1. **Start Agent Zero:**
   ```bash
   cd agent-zero
   python run_cli.py
   ```

2. **Test DXF Generation:**
   ```
   User: Generate a floor plan for a 2-bedroom house with kitchen

   Agent: I'll create a floor plan for a 2-bedroom house with kitchen using the DXF generator.

   [Agent uses generate_architectural_dxf tool]

   Agent: ✅ I've generated a DXF floor plan for your 2-bedroom house!
   
   📝 Description: 2-bedroom house with kitchen
   📏 Scale: 1.0
   🏢 Building type: house  
   🔗 Download: [URL]
   
   The DXF file includes:
   - Residential layout (8m x 6m)
   - Interior walls separating bedrooms and kitchen
   - Door and window placements
   - Room labels and dimensions
   
   You can open this in AutoCAD, FreeCAD, or any CAD software.
   ```

### Troubleshooting

**Common Issues:**

1. **MCP Connection Failed:**
   - Check file paths in configuration
   - Verify environment variables are set
   - Ensure mcp dependencies are installed

2. **Appwrite Upload Errors:**
   - Verify API key has proper permissions
   - Check bucket exists and is configured correctly
   - Ensure endpoint URL is correct

3. **Agent Zero Not Finding Tools:**
   - Check MCP server configuration in agent config
   - Verify server starts without errors
   - Test with `python test_mcp.py`

## 📊 Monitoring & Logs

### Railway Logs
Monitor your deployment:
```bash
# View Railway logs
railway logs

# Follow logs in real-time
railway logs --follow
```

### Agent Zero Logs
Check Agent Zero logs for MCP interactions:
```bash
# In agent-zero directory
tail -f logs/agent.log
```

## 🔒 Security Best Practices

1. **Environment Variables:**
   - Never commit secrets to Git
   - Use Railway's secure environment variables
   - Rotate API keys regularly

2. **Appwrite Security:**
   - Use read-only tokens where possible
   - Set proper bucket permissions
   - Monitor file upload limits

3. **Agent Permissions:**
   - Limit MCP server access to specific directories
   - Monitor tool usage and file generation
   - Set reasonable limits on file sizes

---

## 🎯 Quick Start Checklist

- [ ] Repository deployed to Railway
- [ ] Environment variables configured  
- [ ] Appwrite storage set up
- [ ] Agent Zero installed locally
- [ ] MCP server running locally
- [ ] Agent Zero configured with MCP server
- [ ] Test: "Generate a floor plan" works
- [ ] DXF files download correctly

**🎉 Ready to generate CAD drawings with AI!** 