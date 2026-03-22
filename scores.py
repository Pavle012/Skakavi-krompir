"""
scores.py  —  Local and public leaderboard rendered as pygame overlays.
No tkinter/customtkinter required.
"""

import os
import ast
import dependencies
import requests
import pygame_ui

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


def start():
    """Display local scores as a pygame overlay."""
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

    if scores:
        top_idx = scores.index(max(scores))
        top_score = scores[top_idx]
        top_name = names[top_idx]
        top_date = dates[top_idx]
    else:
        top_score, top_name, top_date = 0, "Nobody", "the creation of the project"

    extra_info = [f"Top: {top_score} by {top_name} on {top_date}"]

    # Build rows sorted by score descending
    sorted_entries = sorted(zip(scores, names, dates), reverse=True)
    rows = [(str(s), n, d) for s, n, d in sorted_entries]

    columns = [
        ("Score", 0.25),
        ("Name", 0.35),
        ("Date", 0.40),
    ]

    # Extra button to open public leaderboard — we use the return value
    action_buttons = [
        {"label": "Public", "color": (52, 100, 180), "hover": (40, 80, 150), "value": "public"}
    ]

    result = pygame_ui.draw_scrollable_list(
        title="Local Scores",
        rows=rows,
        columns=columns,
        action_buttons_per_row=action_buttons if rows else [],
        close_label="Close",
        extra_info=extra_info,
    )

    # If the user clicked "Public" on any row, open the public leaderboard
    if result is not None:
        _row_idx, btn_value = result
        if btn_value == "public":
            start_public()

    # Regardless, show public leaderboard button on empty list too
    if not rows:
        # No scores yet; offer a shortcut
        screen = pygame_ui._get_screen()
        pygame_ui.draw_scrollable_list(
            title="Local Scores",
            rows=[],
            columns=[("Score", 0.33), ("Name", 0.33), ("Date", 0.34)],
            extra_info=["No local scores yet!", "Play a game to record your first score."],
        )


def start_public():
    """Display the public leaderboard as a pygame overlay."""
    leaderboard_data = get_leaderboard()

    if leaderboard_data:
        sorted_lb = sorted(leaderboard_data, key=lambda x: x["score"], reverse=True)
        rows = [(str(e["score"]), e["player"]) for e in sorted_lb]
        extra = []
    else:
        rows = []
        extra = ["Could not fetch leaderboard. Check your connection."]

    columns = [
        ("Score", 0.35),
        ("Player", 0.65),
    ]

    pygame_ui.draw_scrollable_list(
        title="Public Leaderboard",
        rows=rows,
        columns=columns,
        extra_info=extra,
    )
