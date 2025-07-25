import tkinter as tk

def lose_screen():
    root = tk.Tk()
    loselabel = tk.Label(root, text="You lost!", font=("assets/Poppins.ttf", 24))
    loselabel.pack()
    root.mainloop()
    root.title("skakavi krompir")
    root.geometry("300x200")
