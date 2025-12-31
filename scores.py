import pygame
import pygame_gui
import os
import ast
import dependencies
import dependencies
import sys

if sys.platform == "emscripten":
    requests = None
else:
    try:
        import requests
    except ImportError:
        requests = None

# --- Public Leaderboard Config ---
SERVER_URL = "https://dragon-honest-directly.ngrok-free.app"
SECRET_KEY = "GhrMYxwtogB8"

# --- UI Window Globals ---
scores_window = None
public_leaderboard_window = None

def submit_score(player, score):
    """Submits a score to the public leaderboard."""
    if requests is None:
        print("Network disabled or requests module missing.")
        return
    if not player:
        print("Cannot submit score for empty player name.")
        return
    payload = {"player": player, "score": score, "secret": SECRET_KEY}
    try:
        r = requests.post(f"{SERVER_URL}/submit", json=payload, timeout=5)
        r.raise_for_status()
        print("Submit response:", r.json())
    except requests.exceptions.RequestException as e:
        print("Error submitting score:", e)

def get_leaderboard(limit=15):
    """Fetches the public leaderboard."""
    if requests is None:
        print("Network disabled or requests module missing.")
        return None
    try:
        r = requests.get(f"{SERVER_URL}/leaderboard", params={"limit": limit}, timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        print("Error fetching leaderboard:", e)
        return None

def create_scores_window(manager):
    """Creates the local scores window using pygame_gui."""
    global scores_window
    if scores_window is not None:
        scores_window.focus()
        return
    
    scores_window = pygame_gui.elements.UIWindow(
        rect=pygame.Rect((0, 0), (500, 500)),
        manager=manager,
        window_display_title="Local Scores"
    )
    scores_window.rect.center = (manager.window_resolution[0] // 2, manager.window_resolution[1] // 2)

    scores_path = os.path.join(dependencies.get_user_data_dir(), "scores.txt")
    if not os.path.exists(scores_path):
        open(scores_path, "w").close()

    scores_data = []
    with open(scores_path) as f:
        for line in f:
            try:
                score_entry = ast.literal_eval(line.strip())
                if len(score_entry) == 3:
                    scores_data.append(score_entry)
            except (ValueError, SyntaxError):
                pass
    
    # Sort by score descending
    sorted_scores = sorted(scores_data, key=lambda x: x[0], reverse=True)

    # Format scores as HTML for the text box
    html_text = "<b><u>Local Scores</u></b><br><br>"
    if not sorted_scores:
        html_text += "<i>No scores recorded yet.</i>"
    else:
        top_score = sorted_scores[0]
        html_text += f"<b>Top Score: {top_score[0]} by {top_score[1]} on {top_score[2]}</b><br><br>"
        for s, n, d in sorted_scores:
            html_text += f"{s} — {n} ({d})<br>"

    pygame_gui.elements.UITextBox(
        relative_rect=scores_window.get_container().get_rect().inflate(-20, -20),
        html_text=html_text,
        manager=manager,
        container=scores_window
    )

def create_public_leaderboard_window(manager):
    """Creates the public leaderboard window using pygame_gui."""
    global public_leaderboard_window
    if public_leaderboard_window is not None:
        public_leaderboard_window.focus()
        return
    
    public_leaderboard_window = pygame_gui.elements.UIWindow(
        rect=pygame.Rect((0, 0), (500, 500)),
        manager=manager,
        window_display_title="Public Leaderboard"
    )
    public_leaderboard_window.rect.center = (manager.window_resolution[0] // 2, manager.window_resolution[1] // 2)

    leaderboard_data = get_leaderboard()
    html_text = "<b><u>Public Leaderboard</u></b><br><br>"

    if leaderboard_data:
        sorted_leaderboard = sorted(leaderboard_data, key=lambda x: x['score'], reverse=True)
        for entry in sorted_leaderboard:
            html_text += f"{entry['score']} — {entry['player']}<br>"
    else:
        html_text += "<i>Could not fetch leaderboard data.</i>"
        
    pygame_gui.elements.UITextBox(
        relative_rect=public_leaderboard_window.get_container().get_rect().inflate(-20, -20),
        html_text=html_text,
        manager=manager,
        container=public_leaderboard_window
    )