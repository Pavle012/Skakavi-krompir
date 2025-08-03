import customtkinter as ctk
from customtkinter import filedialog
import shutil

def start():
    def getSettings(key):
        settings = {}
        with open("settings.txt") as f:
            for line in f:
                if "=" in line:
                    k, value = line.strip().split("=", 1)
                    settings[k] = value
        return settings.get(key)


    def setSettings(key, newValue):
        settings = {}
        with open("settings.txt") as f:
            for line in f:
                if "=" in line:
                    k, value = line.strip().split("=", 1)
                    settings[k] = value
        settings[key] = newValue
        with open("settings.txt", "w") as f:
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
            shutil.copyfile(file_path, "assets/font.ttf")
            # subprocess.run(["cp", file_path, "assets/font.ttf"])    # this is deprecated and doesnt work on windows
    def upload_image():
        file_path = filedialog.askopenfilename(
            initialdir="/",
            title="Select an Image File",
            filetypes=(("Transparent image files", "*.png*"), ("All files", "*.*"))
        )
        
        if file_path:
            shutil.copyfile(file_path, "assets/potato.png")
            # subprocess.run(["cp", file_path, "assets/potato.png"])  # this is deprecated and doesnt work on windows


    root = ctk.CTk()
    root.iconbitmap("assets/potato.ico")
    settingsLabel = ctk.CTkLabel(root, text="Settings", font=("assets/font.ttf", 24))
    settingsLabel.pack()
    uploadFontButton = ctk.CTkButton(root, text="Upload Font", command=upload_font, font=("assets/font.ttf", 12))
    uploadFontButton.pack()
    uploadImageButton = ctk.CTkButton(root, text="Upload your own potato", command=upload_image, font=("assets/font.ttf", 12))
    uploadImageButton.pack()
    clarifylabel = ctk.CTkLabel(root, text="Speed", font=("assets/font.ttf", 12))
    clarifylabel.pack()
    scrollPixelsPerFrame = ctk.CTkEntry(root, font=("assets/font.ttf", 16))
    try: 
        scrollPixelsPerFrame.insert(0, int(getSettings("scrollPixelsPerFrame")))
    except:
        scrollPixelsPerFrame.insert(0, 2)
        print("Error: scrollPixelsPerFrame not found in settings.txt, using default value of 2")
    scrollPixelsPerFrame.bind("<Return>", handle_enter_key)
    scrollPixelsPerFrame.pack()
    clarifylabel = ctk.CTkLabel(root, text="Jump height", font=("assets/font.ttf", 12))
    clarifylabel.pack()
    jumpVelocity = ctk.CTkEntry(root, font=("assets/font.ttf", 16))
    try:
        jumpVelocity.insert(0, int(getSettings("jumpVelocity")))
    except:
        jumpVelocity.insert(0, 12)
        print("Error: jumpVelocity not found in settings.txt, using default value of 12")
    jumpVelocity.bind("<Return>", lambda event: setSettings("jumpVelocity", jumpVelocity.get()))
    jumpVelocity.pack()


    root.title("skakavi krompir settings")
    root.geometry("300x200")
    root.mainloop()
