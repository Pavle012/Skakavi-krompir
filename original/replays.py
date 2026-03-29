"""
replays.py  —  Replay save/load/display as pygame overlay.
No tkinter/customtkinter required.
"""

import os
import json
import time
from shared import dependencies
from original import pygame_ui


def get_replays_dir():
    """Returns the path to the replays directory, creating it if it doesn't exist."""
    replays_dir = os.path.join(dependencies.get_user_data_dir(), "replays")
    if not os.path.exists(replays_dir):
        os.makedirs(replays_dir)
    return replays_dir


def save_replay(seed, frames, score, name, config):
    """Saves replay data as a JSON file."""
    replays_dir = get_replays_dir()
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"replay_{timestamp}_{score}.json"
    filepath = os.path.join(replays_dir, filename)

    data = {
        "seed": seed,
        "score": score,
        "name": name,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "config": config,
        "frames": frames,
    }

    with open(filepath, "w") as f:
        json.dump(data, f)
    return filename


def list_replays():
    """Returns a list of saved replay files with metadata, newest first."""
    replays_dir = get_replays_dir()
    replays = []
    if not os.path.exists(replays_dir):
        return []

    for filename in os.listdir(replays_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(replays_dir, filename)
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                    replays.append({
                        "filename": filename,
                        "name": data.get("name", "Unknown"),
                        "score": data.get("score", 0),
                        "timestamp": data.get("timestamp", "Unknown"),
                        "data": data,
                    })
            except Exception as e:
                print(f"Error loading replay {filename}: {e}")

    replays.sort(key=lambda x: x["timestamp"], reverse=True)
    return replays


def _copy_to_clipboard(text):
    """Try to copy text to clipboard; silently fail if unavailable."""
    try:
        import pyperclip
        pyperclip.copy(text)
        print("Copied to clipboard.")
        return True
    except ImportError:
        pass
    try:
        import subprocess
        result = subprocess.run(
            ["xclip", "-selection", "clipboard"],
            input=text.encode(),
            capture_output=True,
        )
        if result.returncode == 0:
            print("Copied to clipboard via xclip.")
            return True
    except Exception:
        pass
    try:
        import subprocess
        result = subprocess.run(
            ["xsel", "--clipboard", "--input"],
            input=text.encode(),
            capture_output=True,
        )
        if result.returncode == 0:
            print("Copied to clipboard via xsel.")
            return True
    except Exception:
        pass
    print("Could not copy to clipboard (no pyperclip / xclip / xsel found).")
    return False


def start():
    """
    Displays a pygame dialog to pick a replay.
    Returns the selected replay data dict, or None.
    """
    replays_list = list_replays()

    rows = [
        (str(r["score"]), r["name"], r["timestamp"]) for r in replays_list
    ]

    columns = [
        ("Score", 0.20),
        ("Name", 0.30),
        ("Timestamp", 0.50),
    ]

    action_buttons = [
        {"label": "Watch", "color": (46, 160, 80), "hover": (36, 130, 60), "value": "watch"},
        {"label": "Copy",  "color": (52, 80, 160),  "hover": (40, 60, 130), "value": "copy"},
    ]

    extra_info = [] if replays_list else ["No replays saved yet."]

    while True:
        result = pygame_ui.draw_scrollable_list(
            title="Saved Replays",
            rows=rows,
            columns=columns,
            action_buttons_per_row=action_buttons if replays_list else [],
            extra_info=extra_info,
        )

        if result is None:
            return None  # closed / cancelled

        row_idx, btn_value = result
        replay = replays_list[row_idx]

        if btn_value == "watch":
            return replay["data"]
        elif btn_value == "copy":
            _copy_to_clipboard(json.dumps(replay["data"]))
            # Stay on list after copy
