import os
import json
import time
import customtkinter as ctk
import dependencies
from PIL import Image, ImageTk

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
        "frames": frames
    }
    
    with open(filepath, "w") as f:
        json.dump(data, f)
    return filename

def list_replays():
    """Returns a list of saved replay files with metadata."""
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
                        "data": data
                    })
            except Exception as e:
                print(f"Error loading replay {filename}: {e}")
    
    # Sort by timestamp descending
    replays.sort(key=lambda x: x["timestamp"], reverse=True)
    return replays

def start(root):
    """Displays a dialog to pick a replay. Returns the selected replay data or None."""
    toplevel = ctk.CTkToplevel(root)
    toplevel.title("Saved Replays")
    toplevel.geometry("500x500")
    
    selected_replay = {"data": None}

    def on_select(replay_data):
        selected_replay["data"] = replay_data
        toplevel.destroy()

    # Use the globally loaded icon
    pil_icon = dependencies.get_global_icon_pil()
    if pil_icon:
        icon_photo = ImageTk.PhotoImage(pil_icon)
        toplevel._icon_photo_ref = icon_photo
        toplevel.iconphoto(True, icon_photo)

    ctk.CTkLabel(toplevel, text="Saved Replays", font=(dependencies.get_font_path(), 24)).pack(pady=10)

    scrollable_frame = ctk.CTkScrollableFrame(toplevel, width=450, height=350)
    scrollable_frame.pack(pady=10, padx=10, fill="both", expand=True)

    replays_list = list_replays()

    if not replays_list:
        ctk.CTkLabel(scrollable_frame, text="No replays found.", font=(dependencies.get_font_path(), 14)).pack(pady=20)
    else:
        for replay in replays_list:
            frame = ctk.CTkFrame(scrollable_frame)
            frame.pack(pady=5, padx=5, fill="x")
            
            label_text = f"{replay['score']} pts — {replay['name']} ({replay['timestamp']})"
            ctk.CTkLabel(frame, text=label_text, font=(dependencies.get_font_path(), 12)).pack(side="left", padx=10, pady=5)
            
            def copy_to_clipboard(data):
                root.clipboard_clear()
                root.clipboard_append(json.dumps(data))
                root.update() # now it stays on the clipboard
                
            ctk.CTkButton(
                frame, 
                text="Copy", 
                width=60, 
                fg_color="#34495e",
                hover_color="#2c3e50",
                command=lambda r=replay['data']: copy_to_clipboard(r),
                font=(dependencies.get_font_path(), 10)
            ).pack(side="right", padx=5, pady=5)

            ctk.CTkButton(
                frame, 
                text="Watch", 
                width=80, 
                command=lambda r=replay['data']: on_select(r),
                font=(dependencies.get_font_path(), 12)
            ).pack(side="right", padx=5, pady=5)

    ctk.CTkButton(toplevel, text="Close", command=toplevel.destroy, font=(dependencies.get_font_path(), 14)).pack(pady=10)

    toplevel.lift()
    toplevel.focus_force()
    toplevel.wait_window()

    return selected_replay["data"]
