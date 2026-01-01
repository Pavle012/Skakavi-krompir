from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QScrollArea, QWidget, 
                             QLabel, QPushButton)
from PyQt6.QtCore import Qt
import os
import ast
import dependencies
import requests
import gui

# --- Public Leaderboard Config ---
SERVER_URL = "https://dragon-honest-directly.ngrok-free.app"
SECRET_KEY = "GhrMYxwtogB8"

def submit_score(player, score):
    payload = {"player": player, "score": score, "secret": SECRET_KEY}
    try:
        r = requests.post(f"{SERVER_URL}/submit", json=payload, timeout=5)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Error submitting score:", e)

def get_leaderboard(limit=15):
    try:
        r = requests.get(f"{SERVER_URL}/leaderboard", params={"limit": limit}, timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        print("Error fetching leaderboard:", e)
        return None

def start(root_dummy):
    dialog = gui.EasyDialog("Local Scores", size=(500, 500))
    dialog.add_label("Local Scores", 24)

    scores_path = os.path.join(dependencies.get_user_data_dir(), "scores.txt")
    if not os.path.exists(scores_path):
        open(scores_path, "w").close()

    scores_list = []
    with open(scores_path) as f:
        for line in f:
            try:
                score_entry = ast.literal_eval(line.strip())
                if len(score_entry) == 3:
                    scores_list.append(score_entry)
            except (ValueError, SyntaxError):
                pass
    
    if scores_list:
        scores_list.sort(key=lambda x: x[0], reverse=True)
        top_score, top_name, top_date = scores_list[0]
    else:
        top_score, top_name, top_date = 0, "Nobody", "N/A"

    dialog.add_label(f"Top Score: {top_score} by {top_name}", 14)

    scroll = QScrollArea()
    scroll_content = QWidget()
    scroll_layout = QVBoxLayout(scroll_content)
    
    for s, n, d in scores_list:
        lbl = QLabel(f"{s} — {n} ({d})")
        lbl.setFont(gui.get_common_font(12))
        scroll_layout.addWidget(lbl)
    
    scroll.setWidget(scroll_content)
    scroll.setWidgetResizable(True)
    dialog.layout.addWidget(scroll)

    dialog.add_button("Public Leaderboard", lambda: start_public(None))
    dialog.add_button("Close", dialog.accept)

    dialog.exec()

def start_public(root_dummy):
    dialog = gui.EasyDialog("Public Leaderboard", size=(500, 500))
    dialog.add_label("Public Leaderboard", 24)

    leaderboard_data = get_leaderboard()
    
    scroll = QScrollArea()
    scroll_content = QWidget()
    scroll_layout = QVBoxLayout(scroll_content)

    if leaderboard_data:
        sorted_leaderboard = sorted(leaderboard_data, key=lambda x: x['score'], reverse=True)
        for entry in sorted_leaderboard:
            lbl = QLabel(f"{entry['score']} — {entry['player']}")
            lbl.setFont(gui.get_common_font(12))
            scroll_layout.addWidget(lbl)
    else:
        scroll_layout.addWidget(QLabel("Could not fetch leaderboard."))

    scroll.setWidget(scroll_content)
    scroll.setWidgetResizable(True)
    dialog.layout.addWidget(scroll)

    dialog.add_button("Close", dialog.accept)
    dialog.exec()