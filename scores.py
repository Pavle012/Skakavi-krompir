import tkinter as tk
import os

if not os.path.exists("scores.txt"):
    with open("scores.txt", "w") as f:
        pass

with open("scores.txt", "r") as f:
    lines = f.readlines()

scores = []
for line in lines:
    try:
        scores.append(int(line.strip()))
    except ValueError:
        pass


root = tk.Tk()
root.title("Scores")
root.geometry("300x400")
allscoreslabel = tk.Label(root, text="All Scores", font=("assets/font.ttf", 24))

topscore = max(scores) if scores else 0
topscorelabel = tk.Label(root, text=f"Top Score: {topscore}", font=("assets/font.ttf", 24))
topscorelabel.pack()
allscoreslabel.pack()

for score in sorted(scores):
    label = tk.Label(root, text=score, font=("assets/font.ttf", 16))
    label.pack()

root.mainloop()
