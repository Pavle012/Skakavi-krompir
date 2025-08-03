import customtkinter as ctk
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
    
    root = ctk.CTk()
    root.iconbitmap("assets/potato.ico")
    loselabel = ctk.CTkLabel(root, text="You lost!", font=("assets/font.ttf", 24))
    loselabel.pack()
    root.title("skakavi krompir")
    root.geometry("300x200")
    exitbutton = ctk.CTkButton(root, text="Exit", command=exit_game, font=("assets/font.ttf", 16))
    restartbutton = ctk.CTkButton(root, text="Restart", command=restart, font=("assets/font.ttf", 16))
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
    root = ctk.CTk()
    root.iconbitmap("assets/potato.ico")
    pauselabel = ctk.CTkLabel(root, text="Paused", font=("assets/font.ttf", 24))
    pauselabel.pack()
    root.title("skakavi krompir")
    root.geometry("340x300")
    exitbutton = ctk.CTkButton(root, text="Exit", command=exit_game, font=("assets/font.ttf", 16))
    resumebutton = ctk.CTkButton(root, text="Resume", command=resume, font=("assets/font.ttf", 16))
    settingsbutton = ctk.CTkButton(root, text="Settings", command=settings, font=("assets/font.ttf", 16))
    scorebutton = ctk.CTkButton(root, text="Scores", command=scores, font=("assets/font.ttf", 16))
    scorebutton.pack()
    resumebutton.pack()
    exitbutton.pack()
    settingsbutton.pack()
    root.mainloop()
    return returncode
