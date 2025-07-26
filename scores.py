import tkinter as tk
import os
import ast

def start():
    if not os.path.exists("scores.txt"):
        open("scores.txt", "w").close()

    scores, names, dates = [], [], []
    with open("scores.txt") as f:
        for line in f:
            try:
                score_entry = ast.literal_eval(line.strip())
                if len(score_entry) == 3:
                    scores.append(score_entry[0])
                    names.append(score_entry[1])
                    dates.append(score_entry[2])
            except (ValueError, SyntaxError):
                pass

    root = tk.Tk()
    root.title("Scores")
    root.geometry("500x500")

    if scores:
        top_idx = scores.index(max(scores))
        top_score = scores[top_idx]
        top_name = names[top_idx]
        top_date = dates[top_idx]
    else:
        top_score, top_name, top_date = 0, "Nobody", "the creation of the project"

    tk.Label(root, text="All Scores", font=("assets/font.ttf", 24)).pack(pady=10)
    tk.Label(
        root,
        text=f"Top Score: {top_score} by {top_name} at {top_date}",
        font=("assets/font.ttf", 14)
    ).pack(pady=5)

    for s, n, d in sorted(zip(scores, names, dates), reverse=True):
        tk.Label(root, text=f"{s} — {n} ({d})", font=("assets/font.ttf", 12)).pack()

    root.mainloop()

if __name__ == "__main__":
    start()
