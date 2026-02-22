import customtkinter as ctk
import dependencies
import os
import tkinter
from PIL import Image, ImageTk

retun = "Unnamed"
def getname(root):
    toplevel = ctk.CTkToplevel(root)
    toplevel.title("Enter Your Name")
    toplevel.geometry("300x200")
    
    def retuna():
        global retun
        retun = entry.get()
        toplevel.destroy()
    
    # Use the globally loaded icon
    pil_icon = dependencies.get_global_icon_pil()
    if pil_icon:
        icon_photo = ImageTk.PhotoImage(pil_icon)
        toplevel._icon_photo_ref = icon_photo # Keep a strong reference
        toplevel.iconphoto(True, icon_photo)

    
    label = ctk.CTkLabel(toplevel, text="Please enter your name:", font=(dependencies.get_font_path(), 16))
    label.pack()
    entry = ctk.CTkEntry(toplevel, font=(dependencies.get_font_path(), 12))
    entry.pack()
    rememberCheck = ctk.CTkCheckBox(toplevel, text="Remember name", font=(dependencies.get_font_path(), 12))
    rememberCheck.pack()
    done_button = ctk.CTkButton(toplevel, text="Save", command=retuna, font=(dependencies.get_font_path(), 12))
    done_button.pack()
    exit_button = ctk.CTkButton(toplevel, text="Exit", command=toplevel.destroy, font=(dependencies.get_font_path(), 12))
    exit_button.pack()
    toplevel.bind('<Return>', lambda event: retuna())
    toplevel.bind('<Escape>', lambda event: toplevel.destroy())
    toplevel.focus_set()
    
    import time
    while toplevel.winfo_exists():
        try:
            root.update_idletasks()
            root.update()
        except:
            break
        time.sleep(0.01)

    def setSettings(key, newValue):
        settings = {}
        settings_path = os.path.join(dependencies.get_user_data_dir(), "settings.txt")
        if os.path.exists(settings_path):
            with open(settings_path) as f:
                for line in f:
                    if "=" in line:
                        k, value = line.strip().split("=", 1)
                        settings[k] = value
        settings[key] = newValue
        with open(settings_path, "w") as f:
            for k, value in settings.items():
                f.write(f"{k}={value}\n")
    
    if rememberCheck.get():
        setSettings("rememberName", "True")
        setSettings("name", retun)
    else:
        setSettings("rememberName", "False")
    
    return retun
