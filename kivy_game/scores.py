"""
scores.py — Local and public leaderboard rendered as Kivy overlays.
"""

import os
import ast
import json
from shared import dependencies

from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock

SERVER_URL = "https://dragon-honest-directly.ngrok-free.app"
SECRET_KEY = "GhrMYxwtogB8"

def submit_score(player, score):
    """Submits a score asynchronously."""
    payload = {"player": player, "score": score, "secret": SECRET_KEY}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    req = UrlRequest(f"{SERVER_URL}/submit", req_body=json.dumps(payload), req_headers=headers)

class ScrollableListModal(ModalView):
    def __init__(self, title, rows, columns, action_buttons_per_row=None, extra_info=None, on_action=None, **kwargs):
        super().__init__(**kwargs)
        self.background_color = [0, 0, 0, 150/255.0]
        self.size_hint = (0.8, 0.9)
        self.auto_dismiss = False
        self.on_action = on_action

        with self.canvas.before:
            Color(30/255, 30/255, 40/255, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
            Color(1, 1, 1, 1)
            self.line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 20), width=2)
            
        self.bind(pos=self.update_graphics, size=self.update_graphics)
        
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        title_label = Label(text=title, font_size=48, bold=True, size_hint_y=None, height=60, color=(1,1,1,1))
        main_layout.add_widget(title_label)
        
        if extra_info:
            for info in extra_info:
                main_layout.add_widget(Label(text=info, font_size=24, size_hint_y=None, height=40))
                
        # Headers
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        for col_name, col_width in columns:
            header_layout.add_widget(Label(text=f"[b]{col_name}[/b]", markup=True, font_size=24, size_hint_x=col_width))
        if action_buttons_per_row:
             # Add space for buttons
             header_layout.add_widget(Label(text="Action", font_size=24, size_hint_x=0.2))
        main_layout.add_widget(header_layout)

        # Rows
        scroll = ScrollView(size_hint_y=1)
        grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        for idx, row in enumerate(rows):
            row_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            for i, (col_name, col_width) in enumerate(columns):
                 row_box.add_widget(Label(text=str(row[i]), font_size=20, size_hint_x=col_width))
                 
            if action_buttons_per_row:
                btn_box = BoxLayout(orientation='horizontal', size_hint_x=0.2, spacing=5)
                for btn_def in action_buttons_per_row:
                    v = btn_def["value"]
                    btn = Button(text=btn_def["label"], background_color=[c/255.0 for c in btn_def["color"]]+[1])
                    def make_cb(row_index, action_val):
                        def cb(instance):
                            self.dismiss()
                            if self.on_action:
                                self.on_action(row_index, action_val)
                        return cb
                    btn.bind(on_release=make_cb(idx, v))
                    btn_box.add_widget(btn)
                row_box.add_widget(btn_box)

            grid.add_widget(row_box)
            
        scroll.add_widget(grid)
        main_layout.add_widget(scroll)
        
        # Add public button if no rows exist but local context
        if not rows and not action_buttons_per_row:
             # Provide way to public if we are local
             if title == "Local Scores":
                 pub_btn = Button(text="Open Public Leaderboard", size_hint=(None, None), size=(300, 50), pos_hint={'center_x': 0.5}, background_color=(52/255, 100/255, 180/255, 1))
                 def on_pub(instance):
                     self.dismiss()
                     if self.on_action: self.on_action(-1, "public")
                 pub_btn.bind(on_release=on_pub)
                 main_layout.add_widget(pub_btn)
        
        btn_close = Button(text="Close", size_hint=(None, None), size=(200, 50), pos_hint={'center_x': 0.5}, background_color=(231/255, 76/255, 60/255, 1))
        btn_close.bind(on_release=self.dismiss)
        main_layout.add_widget(btn_close)
        
        self.add_widget(main_layout)

    def update_graphics(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.line.rounded_rectangle = (self.x, self.y, self.width, self.height, 20)


def start():
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

    sorted_entries = sorted(zip(scores, names, dates), reverse=True)
    rows = [(str(s), n, d) for s, n, d in sorted_entries]

    columns = [("Score", 0.25), ("Name", 0.35), ("Date", 0.40)]

    action_buttons = [{"label": "Public", "color": (52, 100, 180), "value": "public"}]

    def on_row_action(idx, val):
        if val == "public":
            start_public()

    if not rows:
        extra_info = ["No local scores yet!", "Play a game to record your first score."]
    
    modal = ScrollableListModal(
        title="Local Scores",
        rows=rows,
        columns=columns,
        action_buttons_per_row=action_buttons if rows else None,
        extra_info=extra_info,
        on_action=on_row_action
    )
    modal.open()

def start_public():
    def on_success(req, result):
        if result:
            sorted_lb = sorted(result, key=lambda x: x["score"], reverse=True)
            rows = [(str(e["score"]), e["player"]) for e in sorted_lb]
            extra = []
        else:
            rows = []
            extra = ["Could not parse leaderboard."]

        columns = [("Score", 0.35), ("Player", 0.65)]
        
        modal = ScrollableListModal(
            title="Public Leaderboard",
            rows=rows,
            columns=columns,
            extra_info=extra
        )
        modal.open()

    def on_error(req, error):
        modal = ScrollableListModal(
            title="Public Leaderboard",
            rows=[],
            columns=[("Score", 0.35), ("Player", 0.65)],
            extra_info=["Could not fetch leaderboard. Check your connection."]
        )
        modal.open()

    # Create a loading modal
    loading = ScrollableListModal("Public Leaderboard", [], [], extra_info=["Loading..."])
    loading.open()
    
    def on_real_success(req, result):
        loading.dismiss()
        on_success(req, result)
        
    def on_real_error(req, error):
        loading.dismiss()
        on_error(req, error)
        
    UrlRequest(f"{SERVER_URL}/leaderboard?limit=15", on_success=on_real_success, on_error=on_real_error, on_failure=on_real_error)
