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
    """GET endpoint for Agent Zero to verify service status"""
    return {
        "service": "DXF Generator",
        "status": "active",
        "description": "Genera archivos DXF arquitectónicos desde descripciones de texto",
        "endpoint": "/",
        "method": "POST",
        "required_fields": ["prompt"],
        "response_type": "text/event-stream",
        "example": {
            "prompt": "casa con 2 puertas y 3 ventanas"
        },
        "version": "1.0"
    }

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
    """Health check endpoint for Agent Zero"""
    return {"status": "healthy", "service": "dxf-generator"}


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
