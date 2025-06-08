from flask import Flask, Response, request, stream_with_context, send_file
import ezdxf
import os
import uuid
import json

app = Flask(__name__)

# Create uploads directory for storing DXF files
os.makedirs("uploads", exist_ok=True)
print("✅ Railway deployment ready - no external dependencies needed!")



def draw_architectural_plan(doc, prompt_text):
    msp = doc.modelspace()
    msp.add_lwpolyline([
        (0, 0), (6000, 0), (6000, 4000), (0, 4000), (0, 0)
    ], dxfattribs={"closed": True})
    msp.add_text(prompt_text, dxfattribs={'height': 250, 'layer': 'TEXT'}).set_pos((100, 3800), align='LEFT')

@app.route("/", methods=["GET"])
def service_info():
    """GET endpoint for Agent Zero to verify service status - returns SSE format"""
    def info_stream():
        yield "data: {\"service\": \"DXF Generator\", \"status\": \"active\"}\n\n"
        yield "data: {\"description\": \"Genera archivos DXF arquitectónicos\"}\n\n"
        yield "data: {\"ready\": true, \"version\": \"1.0\"}\n\n"
    
    return Response(info_stream(), content_type="text/event-stream")

@app.route("/", methods=["POST"])
def generate_dxf():
    def event_stream():
        try:
            data = request.get_json()
            if not data or "prompt" not in data:
                yield f"data: {json.dumps({'text': ' Falta el campo prompt'})}\n\n"
                return

            prompt = data["prompt"]
            yield f"data: {json.dumps({'text': f' Recibido: {prompt}'})}\n\n"

            # Generate unique filename
            file_id = uuid.uuid4().hex
            filename = f"{file_id}_{prompt.replace(' ', '_')[:30]}.dxf"
            
            # Create DXF file
            doc = ezdxf.new()
            draw_architectural_plan(doc, prompt)

            # Save to uploads directory
            file_path = os.path.join("uploads", filename)
            doc.saveas(file_path)
            yield f"data: {json.dumps({'text': ' DXF generado'})}\n\n"

            # Create download URL (Railway will serve this)
            download_url = f"/download/{filename}"
            yield f"data: {json.dumps({'text': ' Archivo listo', 'url': download_url})}\n\n"
            yield f"data: {json.dumps({'text': ' ✅ Archivo disponible para descarga'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(stream_with_context(event_stream()), content_type="text/event-stream")


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for Agent Zero - returns SSE format"""
    def health_stream():
        yield "data: {\"status\": \"healthy\", \"service\": \"dxf-generator\"}\n\n"
    
    return Response(health_stream(), content_type="text/event-stream")


@app.route("/status", methods=["GET"])
def simple_status():
    """Simple JSON status for Agent Zero (non-streaming)"""
    return {"status": "active", "service": "dxf-generator", "ready": True}

@app.route("/mcp", methods=["POST"])
def mcp_endpoint():
    """MCP JSON-RPC endpoint for Agent Zero"""
    try:
        data = request.get_json()
        
        # Handle MCP initialize request
        if data.get("method") == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": data.get("id"),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {
                            "listChanged": True
                        }
                    },
                    "serverInfo": {
                        "name": "dxf-generator",
                        "version": "1.0.0"
                    }
                }
            }
        
        # Handle tools/list request
        elif data.get("method") == "tools/list":
            return {
                "jsonrpc": "2.0", 
                "id": data.get("id"),
                "result": {
                    "tools": [
                        {
                            "name": "generate_dxf",
                            "description": "Genera archivos DXF arquitectónicos desde descripciones de texto",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "prompt": {
                                        "type": "string",
                                        "description": "Descripción del plano arquitectónico"
                                    }
                                },
                                "required": ["prompt"]
                            }
                        }
                    ]
                }
            }
        
        # Handle tools/call request
        elif data.get("method") == "tools/call":
            params = data.get("params", {})
            if params.get("name") == "generate_dxf":
                arguments = params.get("arguments", {})
                prompt = arguments.get("prompt", "")
                
                # Generate DXF file
                file_id = uuid.uuid4().hex
                filename = f"{file_id}_{prompt.replace(' ', '_')[:30]}.dxf"
                
                doc = ezdxf.new()
                draw_architectural_plan(doc, prompt)
                
                file_path = os.path.join("uploads", filename)
                doc.saveas(file_path)
                
                download_url = f"/download/{filename}"
                
                return {
                    "jsonrpc": "2.0",
                    "id": data.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"✅ Archivo DXF generado exitosamente!\n📁 Archivo: {filename}\n🔗 URL de descarga: {download_url}\n📝 Basado en: {prompt}"
                            }
                        ]
                    }
                }
        
        # Default response for unknown methods
        return {
            "jsonrpc": "2.0",
            "id": data.get("id"),
            "error": {
                "code": -32601,
                "message": "Method not found"
            }
        }
        
    except Exception as e:
        return {
            "jsonrpc": "2.0", 
            "id": data.get("id") if data else None,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }


@app.route("/download/<filename>")
def download_file(filename):
    """Serve DXF files for download"""
    try:
        file_path = os.path.join("uploads", filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            return "File not found", 404
    except Exception as e:
        return f"Error: {str(e)}", 500


if __name__ == "__main__":
    # Use Railway's PORT environment variable if available, otherwise default to 80
    port = int(os.environ.get("PORT", 80))
    app.run(host="0.0.0.0", port=port)
