import tkinter as tk
import multiprocessing
returncode = "error"

def lose_screen():
    global returncode
    def exit_game():
        global returncode
        returncode = "exit"
        root.destroy()
    
    def restart():
        global returncode
        returncode = "restart"
        root.destroy()
    
    root = tk.Tk()
    loselabel = tk.Label(root, text="You lost!", font=("assets/Poppins.ttf", 24))
    loselabel.pack()
    root.title("skakavi krompir")
    root.geometry("300x200")
    exitbutton = tk.Button(root, text="Exit", command=exit_game, font=("assets/Poppins.ttf", 16))
    restartbutton = tk.Button(root, text="Restart", command=restart, font=("assets/Poppins.ttf", 16))
    restartbutton.pack()
    exitbutton.pack()
    root.mainloop()
    if returncode == "exit":
        return "exit"
    elif returncode == "restart":
        return "restart"




def pause_screen():
    global returncode
    def exit_game():
        global returncode
        returncode = "exit"
        root.destroy()
    def resume():
        global returncode
        returncode = "resume"
        root.destroy()
    root = tk.Tk()
    pauselabel = tk.Label(root, text="Paused", font=("assets/Poppins.ttf", 24))
    pauselabel.pack()
    root.title("skakavi krompir")
    root.geometry("300x200")
    exitbutton = tk.Button(root, text="Exit", command=exit_game, font=("assets/Poppins.ttf", 16))
    resumebutton = tk.Button(root, text="Resume", command=resume, font=("assets/Poppins.ttf", 16))
    resumebutton.pack()
    exitbutton.pack()
    root.mainloop()
    if returncode == "exit":
        return "exit"
    elif returncode == "resume":
        return "resume"
