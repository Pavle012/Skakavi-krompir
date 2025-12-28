import customtkinter as ctk
import scores as scs
import options
import dependencies
from PIL import Image, ImageTk
returncode = "error"

def lose_screen(root):
    global returncode
    toplevel = ctk.CTkToplevel(root)
    toplevel.title("skakavi krompir")
    toplevel.geometry("300x200")

    def exit_game():
        global returncode
        returncode = "exit"
        toplevel.quit()
        toplevel.destroy()
    
    def restart():
        global returncode
        returncode = "restart"
        toplevel.quit()
        toplevel.destroy()
    
    # Use the globally loaded icon
    pil_icon = dependencies.get_global_icon_pil()
    if pil_icon:
        icon_photo = ImageTk.PhotoImage(pil_icon)
        toplevel._icon_photo_ref = icon_photo # Keep a strong reference
        toplevel.iconphoto(True, icon_photo)
    loselabel = ctk.CTkLabel(toplevel, text="You lost!", font=(dependencies.get_font_path(), 24))
    loselabel.pack()
    
    toplevel.bind("<Return>", lambda e: restart())
    restartbutton = ctk.CTkButton(toplevel, text="Restart", command=restart, font=(dependencies.get_font_path(), 16))
    exitbutton = ctk.CTkButton(toplevel, text="Exit", command=exit_game, font=(dependencies.get_font_path(), 16))
    restartbutton.pack()
    exitbutton.pack()
    toplevel.mainloop()
    if returncode == "exit":
        return "exit"
    elif returncode == "restart":
        return "restart"



def pause_screen(root):
    global returncode
    toplevel = ctk.CTkToplevel(root)
    toplevel.title("skakavi krompir")
    toplevel.geometry("340x300")
    
    def exit_game():
        global returncode
        returncode = "exit"
        toplevel.quit()
        toplevel.destroy()
    def resume():
        global returncode
        returncode = "resume"
        toplevel.quit()
        toplevel.destroy()
    def settings():
        options.start(root)
    def scores():
        scs.start(root)
    
    # Use the globally loaded icon
    pil_icon = dependencies.get_global_icon_pil()
    if pil_icon:
        icon_photo = ImageTk.PhotoImage(pil_icon)
        toplevel._icon_photo_ref = icon_photo # Keep a strong reference
        toplevel.iconphoto(True, icon_photo)
    pauselabel = ctk.CTkLabel(toplevel, text="Paused", font=(dependencies.get_font_path(), 24))
    pauselabel.pack()
    
    toplevel.bind("<Escape>", lambda e: resume())
    scorebutton = ctk.CTkButton(toplevel, text="Scores", command=scores, font=(dependencies.get_font_path(), 16))
    resumebutton = ctk.CTkButton(toplevel, text="Resume", command=resume, font=(dependencies.get_font_path(), 16))
    exitbutton = ctk.CTkButton(toplevel, text="Exit", command=exit_game, font=(dependencies.get_font_path(), 16))
    settingsbutton = ctk.CTkButton(toplevel, text="Settings", command=settings, font=(dependencies.get_font_path(), 16))
    scorebutton.pack()
    resumebutton.pack()
    exitbutton.pack()
    settingsbutton.pack()
    toplevel.mainloop()
    return returncode