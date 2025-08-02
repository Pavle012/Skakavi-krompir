import tkinter as tk
import scores as scs
import options
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
    loselabel = tk.Label(root, text="You lost!", font=("assets/font.ttf", 24))
    loselabel.pack()
    root.title("skakavi krompir")
    root.geometry("300x200")
    exitbutton = tk.Button(root, text="Exit", command=exit_game, font=("assets/font.ttf", 16))
    restartbutton = tk.Button(root, text="Restart", command=restart, font=("assets/font.ttf", 16))
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
    def settings():
        options.start()
    def scores():
        scs.start()
    root = tk.Tk()
    pauselabel = tk.Label(root, text="Paused", font=("assets/font.ttf", 24))
    pauselabel.pack()
    root.title("skakavi krompir")
    root.geometry("340x300")
    exitbutton = tk.Button(root, text="Exit", command=exit_game, font=("assets/font.ttf", 16))
    resumebutton = tk.Button(root, text="Resume", command=resume, font=("assets/font.ttf", 16))
    settingsbutton = tk.Button(root, text="Settings", command=settings, font=("assets/font.ttf", 16))
    scorebutton = tk.Button(root, text="Scores", command=scores, font=("assets/font.ttf", 16))
    scorebutton.pack()
    resumebutton.pack()
    exitbutton.pack()
    settingsbutton.pack()
    root.mainloop()
    return returncode
