from PIL import Image, ImageTk
import customtkinter as ctk
from customtkinter import filedialog
import shutil
import dependencies
import os


def start():
    def getSettings(key):
        settings = {}
        settings_path = os.path.join(dependencies.get_user_data_dir(), "settings.txt")
        if not os.path.exists(settings_path):
            return None
        with open(settings_path) as f:
            for line in f:
                if "=" in line:
                    k, value = line.strip().split("=", 1)
                    settings[k] = value
        return settings.get(key)


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

    def handle_enter_key(event):
        entered_text = scrollPixelsPerFrame.get()
        setSettings("scrollPixelsPerFrame", entered_text)

    def upload_font():
        file_path = filedialog.askopenfilename(
            initialdir="/",
            title="Select a Font File",
            filetypes=(("Font files", "*.ttf"), ("All files", "*.*"))
        )
        
        if file_path:
            shutil.copyfile(file_path, dependencies.resource_path("assets/font.ttf"))
    def upload_image():
        file_path = filedialog.askopenfilename(
            initialdir="/",
            title="Select an Image File",
            filetypes=(("Transparent image files", "*.png*"), ("All files", "*.*"))
        )
        
        if file_path:
            shutil.copyfile(file_path, dependencies.resource_path("assets/potato.png"))
            img = Image.open(dependencies.resource_path("assets/potato.png"))
            img.save(dependencies.resource_path("assets/potato.ico"), format='ICO', sizes=[(64, 64)])
            img.resize((64, 64), Image.NEAREST)
            img.save(dependencies.resource_path("assets/potato.png"), format="PNG")
            


    root = ctk.CTk()
    icon_path = dependencies.resource_path("assets/potato.png")
    icon_image = Image.open(icon_path)
    root.icon_photo = ImageTk.PhotoImage(icon_image)
    root.iconphoto(True, root.icon_photo)
    settingsLabel = ctk.CTkLabel(root, text="Settings", font=(dependencies.resource_path("assets/font.ttf"), 24))
    settingsLabel.pack()
    uploadFontButton = ctk.CTkButton(root, text="Upload Font", command=upload_font, font=(dependencies.resource_path("assets/font.ttf"), 12))
    uploadFontButton.pack()
    uploadImageButton = ctk.CTkButton(root, text="Upload your own potato", command=upload_image, font=(dependencies.resource_path("assets/font.ttf"), 12))
    uploadImageButton.pack()
    
    
    clarifylabel = ctk.CTkLabel(root, text="Speed", font=(dependencies.resource_path("assets/font.ttf"), 12))
    clarifylabel.pack()
    scrollPixelsPerFrame = ctk.CTkEntry(root, font=(dependencies.resource_path("assets/font.ttf"), 16))
    try: 
        scrollPixelsPerFrame.insert(0, int(getSettings("scrollPixelsPerFrame")))
    except:
        scrollPixelsPerFrame.insert(0, 2)
        print("Error: scrollPixelsPerFrame not found in settings.txt, using default value of 2")
    scrollPixelsPerFrame.bind("<Return>", handle_enter_key)
    scrollPixelsPerFrame.pack()
    clarifylabel = ctk.CTkLabel(root, text="Jump height", font=(dependencies.resource_path("assets/font.ttf"), 12))
    clarifylabel.pack()
    jumpVelocity = ctk.CTkEntry(root, font=(dependencies.resource_path("assets/font.ttf"), 16))
    try:
        jumpVelocity.insert(0, int(getSettings("jumpVelocity")))
    except:
        jumpVelocity.insert(0, 12)
        print("Error: jumpVelocity not found in settings.txt, using default value of 12")
    jumpVelocity.bind("<Return>", lambda event: setSettings("jumpVelocity", jumpVelocity.get()))
    jumpVelocity.pack()
    
    
    clarifylabel = ctk.CTkLabel(root, text="Max FPS", font=(dependencies.resource_path("assets/font.ttf"), 12))
    clarifylabel.pack()
    maxFps = ctk.CTkEntry(root, font=(dependencies.resource_path("assets/font.ttf"), 16))
    try:
        maxFps.insert(0, int(getSettings("maxFps")))
    except:
        maxFps.insert(0, 120)
        print("Error: maxFps not found in settings.txt, using default value of 120")
    maxFps.bind("<Return>", lambda event: setSettings("maxFps", maxFps.get()))
    maxFps.pack()
    

    root.title("skakavi krompir settings")
    root.geometry("400x400")
    root.mainloop()