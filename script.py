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


# Load setlist with order from setlist_order.txt (if it exists)
def load_setlist_with_order(project_path):
    markers = load_markers(project_path)
    order_file = os.path.join(project_path, "setlist_order.txt")

    if os.path.exists(order_file):
        with open(order_file, "r") as f:
            order = [line.strip() for line in f if line.strip()]
        ordered_markers = []
        unordered = markers.copy()
        for name in order:
            for m in unordered:
                if m[0] == name:
                    ordered_markers.append(m)
                    unordered.remove(m)
                    break
        return ordered_markers + unordered
    return markers


class ReaperSetApp:
    def __init__(self):
        self.project_path = None
        self.setlist = []
        self.edit_mode = False

        self.root = tk.Tk()
        self.root.title("ReaperSet Setlist")
        self.root.geometry("300x400")

        self.frame = tk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.refresh_button = tk.Button(self.root, text="Refresh", command=self.refresh)
        self.refresh_button.pack(side=tk.BOTTOM, fill=tk.X)

        self.edit_button = tk.Button(self.root, text="Edit Setlist", command=self.toggle_edit_mode)
        self.edit_button.pack(side=tk.BOTTOM, fill=tk.X)

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

    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        self.edit_button.config(text="Save Setlist" if self.edit_mode else "Edit Setlist")
        if not self.edit_mode:
            self.save_setlist()
        self.update_buttons()

    def auto_refresh(self):
        if not self.edit_mode:
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

        self.setlist = load_setlist_with_order(self.project_path)
        self.update_buttons()

    def update_buttons(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

        for i, (name, timecode) in enumerate(self.setlist):
            row = tk.Frame(self.frame)
            row.pack(fill=tk.X, pady=2)

            btn = tk.Button(row, text=name, command=lambda t=timecode: self.jump_to_marker(t))
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

            if self.edit_mode:
                if i > 0:
                    up_btn = tk.Button(row, text="↑", width=3, command=lambda i=i: self.move_marker_up(i))
                    up_btn.pack(side=tk.LEFT)
                if i < len(self.setlist) - 1:
                    down_btn = tk.Button(row, text="↓", width=3, command=lambda i=i: self.move_marker_down(i))
                    down_btn.pack(side=tk.LEFT)

    def save_setlist(self):
        if not self.project_path:
            return
        order_file = os.path.join(self.project_path, "setlist_order.txt")
        try:
            with open(order_file, "w") as f:
                for name, _ in self.setlist:
                    f.write(f"{name}\n")
            print(f"Saved setlist order to {order_file}")
        except Exception as e:
            print(f"Error saving setlist: {e}")

    def jump_to_marker(self, time_seconds):
        client.send_message("/time", time_seconds)
        # Ask REAPER if it is playing
        import subprocess
        is_playing = subprocess.run(
            ['osascript', '-e', 'tell application "REAPER" to return playing'],
            capture_output=True, text=True
        )
        if is_playing.stdout.strip() == "true":
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

    def move_marker_up(self, index):
        self.setlist[index - 1], self.setlist[index] = self.setlist[index], self.setlist[index - 1]
        self.update_buttons()

    def move_marker_down(self, index):
        self.setlist[index], self.setlist[index + 1] = self.setlist[index + 1], self.setlist[index]
        self.update_buttons()


if __name__ == "__main__":
    ReaperSetApp()