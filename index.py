"""Flask UI for the steganography tool. Routes: / , /api/capacity, /api/encode, /api/decode"""
import io
from flask import Flask, render_template, request, send_file, jsonify
from stego_engine import encode, decode, get_image_capacity

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 4 * 1024 * 1024  # Vercel rejects bodies over ~4.5 MB anyway


@app.errorhandler(ValueError)
@app.errorhandler(OSError)  # PIL.UnidentifiedImageError (not an image) lands here
def bad_input(e):
    return jsonify(error=str(e)), 400


def upload():
    f = request.files.get("image")
    if not f:
        raise ValueError("Please choose an image.")
    return f.stream


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/capacity", methods=["POST"])
def capacity():
    return jsonify(capacity=get_image_capacity(upload()))


@app.route("/api/encode", methods=["POST"])
def api_encode():
    img, message = upload(), request.form.get("message", "")
    if not message.strip():
        raise ValueError("Please enter a secret message.")
    buf = io.BytesIO()
    s = encode(img, message, buf)
    buf.seek(0)
    resp = send_file(buf, mimetype="image/png", as_attachment=True, download_name="stego_output.png")
    resp.headers["X-Stats"] = f"{s['message_length']}|{s['bits_used']}|{s['max_capacity']}|{s['utilisation_pct']}"
    resp.headers["Access-Control-Expose-Headers"] = "X-Stats"
    return resp


@app.route("/api/decode", methods=["POST"])
def api_decode():
    message = decode(upload())
    if message:
        return jsonify(message=message)
    return jsonify(message="", warning="No hidden message found in this image.")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
