FROM python:3.12-slim

WORKDIR /app

# Removing Node.js installation to reduce build complexity
# RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main service file
COPY main.py .
# COPY mcp_server.py .

# Expose port for HTTP service (backward compatibility)
EXPOSE 80

# Default to the working HTTP server for now
# TODO: Enable MCP server once the library is stable
CMD ["python", "main.py"]
