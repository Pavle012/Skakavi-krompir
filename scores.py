import customtkinter as ctk
import os
import ast
import dependencies
from PIL import Image, ImageTk

def start(root):
    toplevel = ctk.CTkToplevel(root)
    toplevel.title("Scores")
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

    
    # Use the globally loaded icon
    pil_icon = dependencies.get_global_icon_pil()
    if pil_icon:
        icon_photo = ImageTk.PhotoImage(pil_icon)
        toplevel._icon_photo_ref = icon_photo # Keep a strong reference
        toplevel.iconphoto(True, icon_photo)
    

    if scores:
        top_idx = scores.index(max(scores))
        top_score = scores[top_idx]
        top_name = names[top_idx]
        top_date = dates[top_idx]
    else:
        top_score, top_name, top_date = 0, "Nobody", "the creation of the project"

    ctk.CTkLabel(toplevel, text="All Scores", font=(dependencies.get_font_path(), 24)).pack(pady=10)
    ctk.CTkLabel(
        toplevel,
        text=f"Top Score: {top_score} by {top_name} at {top_date}",
        font=(dependencies.get_font_path(), 14)
    ).pack(pady=5)

    for s, n, d in sorted(zip(scores, names, dates), reverse=True):
        ctk.CTkLabel(toplevel, text=f"{s} — {n} ({d})", font=(dependencies.get_font_path(), 12)).pack()

    toplevel.grab_set()
    toplevel.wait_window()