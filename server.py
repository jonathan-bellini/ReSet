from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pythonosc.udp_client import SimpleUDPClient
import os
import json
import webbrowser
import threading

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


# Songs endpoint: expose regions as songs and markers as sections
@app.route("/songs", methods=["GET"])
def get_songs():
    project_file = os.path.expanduser("~/Library/Application Support/REAPER/current_project_path.txt")
    if not os.path.exists(project_file):
        return jsonify({"error": "No project path found"}), 404

    with open(project_file, "r") as f:
        project_path = f.read().strip()

    region_file = os.path.join(project_path, "regions.txt")
    marker_file = os.path.join(project_path, "markers.txt")
    if not os.path.exists(region_file):
        return jsonify({"error": "No regions.txt found"}), 404
    if not os.path.exists(marker_file):
        return jsonify({"error": "No markers.txt found"}), 404

    # Load regions
    regions = []
    with open(region_file, "r") as f:
        for line in f:
            parts = line.strip().split("|")
            if len(parts) != 3:
                continue
            try:
                start = float(parts[0])
                length = float(parts[1])
                title = parts[2].strip()
                regions.append({
                    "title": title,
                    "time": start,
                    "end": start + length,
                    "sections": []
                })
            except Exception as e:
                print(f"Error parsing region: {line} - {e}")

    # Load markers
    markers = []
    with open(marker_file, "r") as f:
        for line in f:
            if "|" not in line:
                continue
            try:
                timecode, label = line.strip().split("|", 1)
                markers.append({"label": label.strip(), "time": float(timecode.strip())})
            except Exception as e:
                print(f"Error parsing marker: {line} - {e}")

    # Assign markers to regions
    for region in regions:
        region["sections"] = [
            m for m in markers if region["time"] <= m["time"] < region["end"]
        ]

    return jsonify(regions)


# Serve index page with song data
@app.route("/")
def index():
    songs = get_song_data()
    return render_template("index.html", songs=songs)


def get_song_data():
    project_file = os.path.expanduser("~/Library/Application Support/REAPER/current_project_path.txt")
    if not os.path.exists(project_file):
        return []

    with open(project_file, "r") as f:
        project_path = f.read().strip()

    json_path = os.path.join(project_path, "structure.json")
    if not os.path.exists(json_path):
        return []

    try:
        with open(json_path, "r") as f:
            return json.load(f)
    except Exception:
        return []

if __name__ == "__main__":
    threading.Timer(1.0, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    app.run(port=5000)