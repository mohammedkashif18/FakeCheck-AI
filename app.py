from flask import Flask, render_template, request, jsonify
from scanner import scan_message, scan_url

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024  # 64 KB input limit

@app.get("/")
def home():
    return render_template("index.html")

@app.post("/api/scan")
def scan():
    data = request.get_json(silent=True) or {}
    scan_type = (data.get("type") or "").strip().lower()
    value = (data.get("value") or "").strip()

    if not value:
        return jsonify({"error": "Please enter a message or URL to scan."}), 400
    if len(value) > 10000:
        return jsonify({"error": "Input is too long. Please keep it under 10,000 characters."}), 400

    if scan_type == "message":
        result = scan_message(value)
    elif scan_type == "url":
        result = scan_url(value)
    else:
        return jsonify({"error": "Unknown scan type."}), 400

    return jsonify(result)

@app.errorhandler(413)
def too_large(_):
    return jsonify({"error": "Request is too large."}), 413

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
