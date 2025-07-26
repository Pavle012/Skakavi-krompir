import tkinter as tk

with open("scores.txt", "r") as f:
    scores = f.readlines()

root = tk.Tk()
root.title("Scores")
root.geometry("300x400")
allscoreslabel = tk.Label(root, text="All Scores", font=("assets/font.ttf", 24))
scores.sort(key=int)

topscorelabel = tk.Label(root, text=f"Top Score: {max(int(score.strip()) for score in scores)}", font=("assets/font.ttf", 24))
topscorelabel.pack()
allscoreslabel.pack()

scores = [int(x) for x in scores]
scores.sort()
for score in scores:
    label = tk.Label(root, text=score, font=("assets/font.ttf", 16))
    label.pack()

root.mainloop()