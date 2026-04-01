"""
replays.py — Replay save/load/display as Kivy overlay.
"""

import os
import json
import time
from shared import dependencies

def get_replays_dir():
    replays_dir = os.path.join(dependencies.get_user_data_dir(), "replays")
    if not os.path.exists(replays_dir):
        os.makedirs(replays_dir)
    return replays_dir

def save_replay(seed, frames, score, name, config):
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
    from kivy.core.clipboard import Clipboard
    Clipboard.copy(text)
    print("Copied to clipboard via Kivy.")
    return True

def start(on_select=None, on_close=None):
    replays_list = list_replays()

    rows = []
    for r in replays_list:
         rows.append((str(r["score"]), r["name"], r["timestamp"]))

    columns = [("Score", 0.20), ("Name", 0.30), ("Timestamp", 0.50)]

    action_buttons = [
        {"label": "Watch", "color": (46, 160, 80), "value": "watch"},
        {"label": "Copy",  "color": (52, 80, 160), "value": "copy"},
    ]

    extra_info = [] if replays_list else ["No replays saved yet."]
    
    def on_action(idx, val):
        if idx >= 0 and idx < len(replays_list):
             replay = replays_list[idx]
             if val == "watch":
                  if on_select:
                       on_select(replay["data"])
             elif val == "copy":
                  _copy_to_clipboard(json.dumps(replay["data"]))
                  start(on_select, on_close) # Re-open since action closes modal by default

    from kivy_game.scores import ScrollableListModal
    modal = ScrollableListModal(
        title="Saved Replays",
        rows=rows,
        columns=columns,
        action_buttons_per_row=action_buttons if replays_list else None,
        extra_info=extra_info,
        on_action=on_action,
        on_close=on_close
    )
    modal.open()
