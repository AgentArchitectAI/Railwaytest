from flask import Flask, Response, request, stream_with_context
import ezdxf
import tempfile
import os
import uuid
import json
from appwrite.client import Client
from appwrite.services.storage import Storage

app = Flask(__name__)

def draw_architectural_plan(doc, prompt_text):
    msp = doc.modelspace()
    msp.add_lwpolyline([
        (0, 0), (6000, 0), (6000, 4000), (0, 4000), (0, 0)
    ], dxfattribs={"closed": True})
    msp.add_text(prompt_text, dxfattribs={'height': 250, 'layer': 'TEXT'}).set_pos((100, 3800), align='LEFT')

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

            filename = prompt.replace(" ", "_") + ".dxf"
            doc = ezdxf.new()
            draw_architectural_plan(doc, prompt)

            temp_path = os.path.join(tempfile.gettempdir(), filename)
            doc.saveas(temp_path)
            yield f"data: {json.dumps({'text': ' DXF generado'})}\n\n"

            client = Client()
            client.set_endpoint(os.environ["APPWRITE_ENDPOINT"])
            client.set_project(os.environ["APPWRITE_PROJECT_ID"])
            client.set_key(os.environ["APPWRITE_API_KEY"])
            storage = Storage(client)

            file_id = uuid.uuid4().hex
            with open(temp_path, "rb") as file:
                storage.create_file(
                    bucket_id=os.environ["APPWRITE_BUCKET_ID"],
                    file_id=file_id,
                    file=file,
                    read=["*"], write=[]
                )

            url = f"{os.environ['APPWRITE_ENDPOINT'].rstrip('/')}/storage/buckets/{os.environ['APPWRITE_BUCKET_ID']}/files/{file_id}/download?project={os.environ['APPWRITE_PROJECT_ID']}"
            yield f"data: {json.dumps({'text': ' Archivo subido', 'url': url})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(stream_with_context(event_stream()), content_type="text/event-stream")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
