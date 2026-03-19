import customtkinter as ctk
import dependencies
import os
import tkinter
from PIL import Image, ImageTk

retun = "Unnamed"
def getname(root):
    # Always keep root hidden and use a Toplevel for the prompt.
    # This is more stable on Linux/Wayland than deiconifying the root.
    root.withdraw()
    
    toplevel = ctk.CTkToplevel(root)
    toplevel.title("Enter Your Name")
    toplevel.geometry("300x250")
    
    # Ensure it stays on top and grabs focus
    toplevel.transient(root)
    toplevel.attributes("-topmost", True)
    
    # We need to wait for it to be mapped before grab_set
    toplevel.wait_visibility()
    toplevel.grab_set()
    
    def retuna():
        global retun
        retun = entry.get()
        toplevel.destroy()
        root.quit()
    
    # Use the globally loaded icon
    pil_icon = dependencies.get_global_icon_pil()
    if pil_icon:
        icon_photo = ImageTk.PhotoImage(pil_icon)
        toplevel._icon_photo_ref = icon_photo # Keep a strong reference
        toplevel.iconphoto(True, icon_photo)

    
    label = ctk.CTkLabel(toplevel, text="Please enter your name:", font=(dependencies.get_font_path(), 16))
    label.pack(pady=10)
    entry = ctk.CTkEntry(toplevel, font=(dependencies.get_font_path(), 12))
    entry.pack(pady=5)
    entry.focus_set()
    
    rememberCheck = ctk.CTkCheckBox(toplevel, text="Remember name", font=(dependencies.get_font_path(), 12))
    rememberCheck.pack(pady=5)
    done_button = ctk.CTkButton(toplevel, text="Save", command=retuna, font=(dependencies.get_font_path(), 12))
    done_button.pack(pady=5)
    
    def on_exit():
        toplevel.destroy()
        root.quit()
            
    exit_button = ctk.CTkButton(toplevel, text="Exit", command=on_exit, font=(dependencies.get_font_path(), 12))
    exit_button.pack(pady=5)
    
    toplevel.protocol("WM_DELETE_WINDOW", on_exit)
    toplevel.bind('<Return>', lambda event: retuna())
    toplevel.bind('<Escape>', lambda event: on_exit())
    
    # Use mainloop for maximum responsiveness during this initial prompt
    root.mainloop()

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
    
    # Check widgets state before they are fully gone if possible, 
    # but since it's modal and we call quit, we should be fine.
    # We'll use a local var to store it before destroy if we have issues.
    
    if rememberCheck.get():
        setSettings("rememberName", "True")
        setSettings("name", retun)
    else:
        setSettings("rememberName", "False")
    
    return retun
