import customtkinter as ctk
import scores as scs
import options
import dependencies
from PIL import Image, ImageTk
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
    icon_path = dependencies.resource_path("assets/potato.png")
    icon_image = Image.open(icon_path)
    root.icon_photo = ImageTk.PhotoImage(icon_image)
    root.iconphoto(True, root.icon_photo)
    loselabel = ctk.CTkLabel(root, text="You lost!", font=(dependencies.resource_path("assets/font.ttf"), 24))
    loselabel.pack()
    root.title("skakavi krompir")
    root.geometry("300x200")
    root.bind("<Return>", lambda e: restart())
    restartbutton = ctk.CTkButton(root, text="Restart", command=restart, font=(dependencies.resource_path("assets/font.ttf"), 16))
    exitbutton = ctk.CTkButton(root, text="Exit", command=exit_game, font=(dependencies.resource_path("assets/font.ttf"), 16))
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
    icon_path = dependencies.resource_path("assets/potato.png")
    icon_image = Image.open(icon_path)
    root.icon_photo = ImageTk.PhotoImage(icon_image)
    root.iconphoto(True, root.icon_photo)
    pauselabel = ctk.CTkLabel(root, text="Paused", font=(dependencies.resource_path("assets/font.ttf"), 24))
    pauselabel.pack()
    root.title("skakavi krompir")
    root.geometry("340x300")
    root.bind("<Escape>", lambda e: resume())
    scorebutton = ctk.CTkButton(root, text="Scores", command=scores, font=(dependencies.resource_path("assets/font.ttf"), 16))
    resumebutton = ctk.CTkButton(root, text="Resume", command=resume, font=(dependencies.resource_path("assets/font.ttf"), 16))
    exitbutton = ctk.CTkButton(root, text="Exit", command=exit_game, font=(dependencies.resource_path("assets/font.ttf"), 16))
    settingsbutton = ctk.CTkButton(root, text="Settings", command=settings, font=(dependencies.resource_path("assets/font.ttf"), 16))
    scorebutton.pack()
    resumebutton.pack()
    exitbutton.pack()
    settingsbutton.pack()
    root.mainloop()
    return returncode