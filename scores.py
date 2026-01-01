import customtkinter as ctk
import os
import ast
import dependencies
from PIL import Image, ImageTk
import requests

# --- Public Leaderboard Config ---
SERVER_URL = "https://dragon-honest-directly.ngrok-free.app"
SECRET_KEY = "GhrMYxwtogB8"

def submit_score(player, score):
    """Submits a score to the public leaderboard."""
    payload = {"player": player, "score": score, "secret": SECRET_KEY}
    try:
        r = requests.post(f"{SERVER_URL}/submit", json=payload, timeout=5)
        r.raise_for_status()
        print("Submit response:", r.json())
    except requests.exceptions.RequestException as e:
        print("Error submitting score:", e)

def get_leaderboard(limit=15):
    """Fetches the public leaderboard."""
    try:
        r = requests.get(f"{SERVER_URL}/leaderboard", params={"limit": limit}, timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        print("Error fetching leaderboard:", e)
        return None

def start(root):
    toplevel = ctk.CTkToplevel(root)
    toplevel.title("Local Scores")
    toplevel.geometry("500x500")

    scores_path = os.path.join(dependencies.get_user_data_dir(), "scores.txt")
    if not os.path.exists(scores_path):
        open(scores_path, "w").close()

    scores, names, dates = [], [], []
    with open(scores_path) as f:
        for line in f:
            try:
                score_entry = ast.literal_eval(line.strip())
                if len(score_entry) == 3:
                    scores.append(score_entry[0])
                    names.append(score_entry[1])
                    dates.append(score_entry[2])
            except (ValueError, SyntaxError):
                pass

    pil_icon = dependencies.get_global_icon_pil()
    if pil_icon:
        icon_photo = ImageTk.PhotoImage(pil_icon)
        toplevel._icon_photo_ref = icon_photo
        toplevel.iconphoto(True, icon_photo)

    if scores:
        top_idx = scores.index(max(scores))
        top_score = scores[top_idx]
        top_name = names[top_idx]
        top_date = dates[top_idx]
    else:
        top_score, top_name, top_date = 0, "Nobody", "the creation of the project"

    ctk.CTkLabel(toplevel, text="Local Scores", font=(dependencies.get_font_path(), 24)).pack(pady=10)
    ctk.CTkLabel(
        toplevel,
        text=f"Top Score: {top_score} by {top_name} at {top_date}",
        font=(dependencies.get_font_path(), 14)
    ).pack(pady=5)

    for s, n, d in sorted(zip(scores, names, dates), reverse=True):
        ctk.CTkLabel(toplevel, text=f"{s} — {n} ({d})", font=(dependencies.get_font_path(), 12)).pack()

    ctk.CTkButton(
        toplevel,
        text="Public Leaderboard",
        command=lambda: start_public(root),
        font=(dependencies.get_font_path(), 12)
    ).pack(pady=10)

    toplevel.wait_window()

def start_public(root):
    """Displays the public leaderboard."""
    public_toplevel = ctk.CTkToplevel(root)
    public_toplevel.title("Public Leaderboard")
    public_toplevel.geometry("500x500")

    pil_icon = dependencies.get_global_icon_pil()
    if pil_icon:
        icon_photo = ImageTk.PhotoImage(pil_icon)
        public_toplevel._icon_photo_ref = icon_photo
        public_toplevel.iconphoto(True, icon_photo)

    ctk.CTkLabel(public_toplevel, text="Public Leaderboard", font=(dependencies.get_font_path(), 24)).pack(pady=10)

    leaderboard_data = get_leaderboard()

    if leaderboard_data:
        # Sort by score descending
        sorted_leaderboard = sorted(leaderboard_data, key=lambda x: x['score'], reverse=True)
        
        for entry in sorted_leaderboard:
            ctk.CTkLabel(
                public_toplevel,
                text=f"{entry['score']} — {entry['player']}",
                font=(dependencies.get_font_path(), 12)
            ).pack()
    else:
        ctk.CTkLabel(public_toplevel, text="Could not fetch leaderboard.", font=(dependencies.get_font_path(), 12)).pack()

    public_toplevel.wait_window()
