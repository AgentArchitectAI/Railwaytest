FROM python:3.12-slim

WORKDIR /app

# Install Node.js for potential MCP server integrations
RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy both the original service and MCP server
COPY main.py .
COPY mcp_server.py .

# Expose port for HTTP service (backward compatibility)
EXPOSE 80

# Default to MCP server, but allow override
# Use environment variable to choose mode: HTTP or MCP
CMD ["python", "mcp_server.py"]
