"""
index.py
────────
Flask web app for the Steganography Tool.
This replaces the Tkinter desktop GUI (app_gui.py) with a browser-based
UI so the project can run on Vercel's serverless Python runtime.

Routes:
    GET  /                 → Web UI (encode + decode tabs)
    POST /api/encode       → Hide a message in an uploaded image, returns PNG
    POST /api/decode       → Extract a hidden message from an uploaded image
    POST /api/capacity     → Return max character capacity for an uploaded image
"""

import io
import base64

from flask import Flask, render_template, request, send_file, jsonify

from stego_engine import encode, decode, get_image_capacity

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB upload limit


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/capacity", methods=["POST"])
def capacity():
    file = request.files.get("image")
    if not file:
        return jsonify({"error": "No image uploaded."}), 400
    try:
        cap = get_image_capacity(file.stream)
        return jsonify({"capacity": cap})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/encode", methods=["POST"])
def api_encode():
    file = request.files.get("image")
    message = request.form.get("message", "")

    if not file:
        return jsonify({"error": "Please choose a carrier image."}), 400
    if not message.strip():
        return jsonify({"error": "Please enter a secret message."}), 400

    try:
        output_buffer = io.BytesIO()
        stats = encode(file.stream, message, output_buffer)
        output_buffer.seek(0)

        # Also embed a base64 preview so the frontend can show the result
        # without a second request.
        preview_b64 = base64.b64encode(output_buffer.getvalue()).decode("ascii")
        output_buffer.seek(0)

        response = send_file(
            output_buffer,
            mimetype="image/png",
            as_attachment=True,
            download_name="stego_output.png",
        )
        response.headers["X-Stats"] = (
            f"{stats['message_length']}|{stats['bits_used']}|"
            f"{stats['max_capacity']}|{stats['utilisation_pct']}"
        )
        response.headers["Access-Control-Expose-Headers"] = "X-Stats"
        return response
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {e}"}), 500


@app.route("/api/decode", methods=["POST"])
def api_decode():
    file = request.files.get("image")
    if not file:
        return jsonify({"error": "Please choose an image to decode."}), 400

    try:
        message = decode(file.stream)
        if message:
            return jsonify({"message": message})
        return jsonify({"message": "", "warning": "No hidden message found in this image."})
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {e}"}), 500


# Local dev entry point (Vercel imports `app` directly and ignores this)
if __name__ == "__main__":
    app.run(debug=True, port=5000)
