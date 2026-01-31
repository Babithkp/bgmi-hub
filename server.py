# server.py
from flask import Flask, jsonify, send_file
import os
import app_state

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "overlay.html")

app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, "static"),
    static_url_path="/static",
)

@app.route("/state")
def state_api():
    return jsonify(app_state.CURRENT_MATCH)

@app.route("/overlay")
def overlay():
    if not os.path.exists(TEMPLATE_PATH):
        return f"overlay.html NOT FOUND at {TEMPLATE_PATH}", 500

    return send_file(TEMPLATE_PATH)