from flask import Flask, request, jsonify
from flask_cors import CORS
from pythonosc.udp_client import SimpleUDPClient

app = Flask(__name__)
CORS(app, origins=["http://127.0.0.1:5500", "http://localhost:5500"])

REAPER_IP = "127.0.0.1"
REAPER_PORT = 8000
client = SimpleUDPClient(REAPER_IP, REAPER_PORT)

@app.route("/jump", methods=["POST"])
def jump_to_time():
    data = request.json
    timecode = data.get("timecode")
    if timecode is not None:
        client.send_message("/time", float(timecode))
        client.send_message("/play", 1)
        return jsonify({"status": "success", "timecode": timecode})
    return jsonify({"status": "error", "message": "No timecode"}), 400

@app.route("/play", methods=["POST"])
def play():
    client.send_message("/play", 1)
    return jsonify({"status": "playing"})

@app.route("/pause", methods=["POST"])
def pause():
    client.send_message("/pause", 1)
    return jsonify({"status": "paused"})

@app.route("/stop", methods=["POST"])
def stop():
    client.send_message("/stop", 1)
    return jsonify({"status": "stopped"})

if __name__ == "__main__":
    app.run(port=5000)