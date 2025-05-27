import os
import time
import tkinter as tk
from pythonosc.udp_client import SimpleUDPClient

REAPER_IP = "127.0.0.1"
REAPER_PORT = 8000

# Adjust this to your REAPER resource path on your system or read dynamically if you want
CURRENT_PROJECT_PATH_FILE = os.path.expanduser(
    "~/Library/Application Support/REAPER/current_project_path.txt"
)

client = SimpleUDPClient(REAPER_IP, REAPER_PORT)


def load_markers(project_path):
    markers = []
    markers_file = os.path.join(project_path, "markers.txt")
    if not os.path.exists(markers_file):
        print(f"Markers file not found: {markers_file}")
        return markers
    with open(markers_file, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    time_str, name = line.split("|", 1)
                    markers.append((name, float(time_str)))
                except Exception as e:
                    print(f"Error parsing marker line: {line} - {e}")
    return markers


class ReaperSetApp:
    def __init__(self):
        self.project_path = None
        self.setlist = []

        self.root = tk.Tk()
        self.root.title("ReaperSet Setlist")
        self.root.geometry("300x400")

        self.frame = tk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.refresh_button = tk.Button(self.root, text="Refresh", command=self.refresh)
        self.refresh_button.pack(side=tk.BOTTOM, fill=tk.X)

        self.controls_frame = tk.Frame(self.root)
        self.controls_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.play_button = tk.Button(self.controls_frame, text="Play", command=self.play)
        self.play_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.pause_button = tk.Button(self.controls_frame, text="Pause", command=self.pause)
        self.pause_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.stop_button = tk.Button(self.controls_frame, text="Stop", command=self.stop)
        self.stop_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.root.after(1000, self.auto_refresh)
        self.root.mainloop()

    def auto_refresh(self):
        self.refresh()
        self.root.after(5000, self.auto_refresh)  # refresh every 5 sec

    def refresh(self):
        if not os.path.exists(CURRENT_PROJECT_PATH_FILE):
            print(f"Waiting for project path file: {CURRENT_PROJECT_PATH_FILE}")
            return

        with open(CURRENT_PROJECT_PATH_FILE, "r") as f:
            project_path = f.read().strip()

        if project_path != self.project_path:
            print(f"Detected new project path: {project_path}")
            self.project_path = project_path

        self.setlist = load_markers(self.project_path)
        self.update_buttons()

    def update_buttons(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        for name, timecode in self.setlist:
            btn = tk.Button(self.frame, text=name, command=lambda t=timecode: self.jump_to_marker(t))
            btn.pack(pady=5, fill=tk.X)

    def jump_to_marker(self, time_seconds):
        client.send_message("/time", time_seconds)
        client.send_message("/play", 1)
        print(f"Jumping to {time_seconds}s")

    def play(self):
        client.send_message("/play", 1)
        print("Playing")

    def pause(self):
        client.send_message("/pause", 1)
        print("Paused")

    def stop(self):
        client.send_message("/stop", 1)
        print("Stopped")


if __name__ == "__main__":
    ReaperSetApp()