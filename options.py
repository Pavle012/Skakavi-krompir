from PIL import Image, ImageTk
import customtkinter as ctk
from customtkinter import filedialog
import shutil
import modloader
import dependencies
import os


def options(root):
    toplevel = ctk.CTkToplevel(root)
    toplevel.title("skakavi krompir settings")
    toplevel.geometry("400x850")

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
            shutil.copyfile(file_path, os.path.join(dependencies.get_user_data_dir(), "font.ttf"))
            # No need to reload anything for the font, it will be used on next app start
    
    def upload_image():
        file_path = filedialog.askopenfilename(
            initialdir="/",
            title="Select an Image File",
            filetypes=(("Transparent image files", "*.png*"), ("All files", "*.*"))
        )
        
        if file_path:
            custom_potato_path = os.path.join(dependencies.get_user_data_dir(), "potato.png")
            custom_ico_path = os.path.join(dependencies.get_user_data_dir(), "potato.ico")
            
            shutil.copyfile(file_path, custom_potato_path)
            
            with Image.open(custom_potato_path) as img:
                img.save(custom_ico_path, format='ICO', sizes=[(64, 64)])
                # The image is already resized by the main game loop, no need to resize here
            
            # Reload the global icon to reflect the change immediately
            dependencies.load_global_icon_pil()
            pil_icon = dependencies.get_global_icon_pil()
            if pil_icon:
                new_icon = ImageTk.PhotoImage(pil_icon)
                toplevel.iconphoto(True, new_icon)
    
    def upload_sound(sound_type):
        file_path = filedialog.askopenfilename(
            initialdir="/",
            title=f"Select {sound_type.capitalize()} Sound File",
            filetypes=(("Audio files", "*.wav *.mp3"), ("All files", "*.*"))
        )
        
        if file_path:
            ext = os.path.splitext(file_path)[1]
            # Use the target name preferred by the game logic
            target_name = f"{sound_type}{ext}"
            # For music, we prefer music.mp3 or music.wav
            # For others we prefer jump.wav, death.wav, etc. (but the game logic check is flexible)
            
            dest_folder = dependencies.get_assets_dir()
            dest_path = os.path.join(dest_folder, target_name)
            
            # Remove existing placeholder if extension differs
            if sound_type != "music":
                old_wav = os.path.join(dest_folder, f"{sound_type}.wav")
                old_mp3 = os.path.join(dest_folder, f"{sound_type}.mp3")
                if os.path.exists(old_wav): os.remove(old_wav)
                if os.path.exists(old_mp3): os.remove(old_mp3)
            else:
                old_wav = os.path.join(dest_folder, "music.wav")
                old_mp3 = os.path.join(dest_folder, "music.mp3")
                if os.path.exists(old_wav): os.remove(old_wav)
                if os.path.exists(old_mp3): os.remove(old_mp3)

            shutil.copyfile(file_path, dest_path)
            print(f"Uploaded {sound_type} to {dest_path}")
            # Note: Sounds are reloaded on next game start/restart
    
    def reset_settings():
        # remove the appdata/.local settings folder
        data_dir = dependencies.get_user_data_dir()
        if os.path.exists(data_dir):
            shutil.rmtree(data_dir)
        dependencies.load_global_icon_pil()
        toplevel.destroy()

    
    # Use the globally loaded icon
    pil_icon = dependencies.get_global_icon_pil()
    if pil_icon:
        icon_photo = ImageTk.PhotoImage(pil_icon)
        toplevel._icon_photo_ref = icon_photo # Keep a strong reference
        toplevel.iconphoto(True, icon_photo)
    settingsLabel = ctk.CTkLabel(toplevel, text="Settings", font=(dependencies.get_font_path(), 24))
    settingsLabel.pack()
    uploadFontButton = ctk.CTkButton(toplevel, text="Upload Font", command=upload_font, font=(dependencies.get_font_path(), 12))
    uploadFontButton.pack()
    uploadImageButton = ctk.CTkButton(toplevel, text="Upload your own potato", command=upload_image, font=(dependencies.get_font_path(), 12))
    uploadImageButton.pack()
    
    # Sound Upload Buttons
    sound_frame = ctk.CTkFrame(toplevel)
    sound_frame.pack(pady=10, fill="x", padx=20)
    ctk.CTkLabel(sound_frame, text="Custom Sounds", font=(dependencies.get_font_path(), 14)).pack()
    
    btn_grid = ctk.CTkFrame(sound_frame)
    btn_grid.pack(pady=5)
    
    ctk.CTkButton(btn_grid, text="Jump", width=80, command=lambda: upload_sound("jump"), font=(dependencies.get_font_path(), 10)).grid(row=0, column=0, padx=2)
    ctk.CTkButton(btn_grid, text="Death", width=80, command=lambda: upload_sound("death"), font=(dependencies.get_font_path(), 10)).grid(row=0, column=1, padx=2)
    ctk.CTkButton(btn_grid, text="Score", width=80, command=lambda: upload_sound("score"), font=(dependencies.get_font_path(), 10)).grid(row=0, column=2, padx=2)
    ctk.CTkButton(btn_grid, text="Powerup", width=80, command=lambda: upload_sound("powerup"), font=(dependencies.get_font_path(), 10)).grid(row=1, column=0, padx=2, pady=2)
    ctk.CTkButton(btn_grid, text="Music", width=80, command=lambda: upload_sound("music"), font=(dependencies.get_font_path(), 10)).grid(row=1, column=1, padx=2, pady=2)
    
    
    clarifylabel = ctk.CTkLabel(toplevel, text="Speed", font=(dependencies.get_font_path(), 12))
    clarifylabel.pack()
    scrollPixelsPerFrame = ctk.CTkEntry(toplevel, font=(dependencies.get_font_path(), 16))
    try: 
        scrollPixelsPerFrame.insert(0, int(getSettings("scrollPixelsPerFrame")))
    except:
        scrollPixelsPerFrame.insert(0, 2)
        print("Error: scrollPixelsPerFrame not found in settings.txt, using default value of 2")
    scrollPixelsPerFrame.bind("<Return>", handle_enter_key)
    scrollPixelsPerFrame.pack()
    clarifylabel = ctk.CTkLabel(toplevel, text="Jump height", font=(dependencies.get_font_path(), 12))
    clarifylabel.pack()
    jumpVelocity = ctk.CTkEntry(toplevel, font=(dependencies.get_font_path(), 16))
    try:
        jumpVelocity.insert(0, int(getSettings("jumpVelocity")))
    except:
        jumpVelocity.insert(0, 12)
        print("Error: jumpVelocity not found in settings.txt, using default value of 12")
    jumpVelocity.bind("<Return>", lambda event: setSettings("jumpVelocity", jumpVelocity.get()))
    jumpVelocity.pack()
    
    
    clarifylabel = ctk.CTkLabel(toplevel, text="Max FPS", font=(dependencies.get_font_path(), 12))
    clarifylabel.pack()
    maxFps = ctk.CTkEntry(toplevel, font=(dependencies.get_font_path(), 16))
    try:
        maxFps.insert(0, int(getSettings("maxFps")))
    except:
        maxFps.insert(0, 120)
        print("Error: maxFps not found in settings.txt, using default value of 120")
    maxFps.bind("<Return>", lambda event: setSettings("maxFps", maxFps.get()))
    maxFps.pack()

    clarifylabel = ctk.CTkLabel(toplevel, text="Speed increase", font=(dependencies.get_font_path(), 12))
    clarifylabel.pack()
    speedIncrease = ctk.CTkEntry(toplevel, font=(dependencies.get_font_path(), 16))
    try:
        speedIncrease.insert(0, int(getSettings("speed_increase")))
    except:
        speedIncrease.insert(0, 3)
        print("Error: speed_increase not found in settings.txt, using default value of 3")
    speedIncrease.bind("<Return>", lambda event: setSettings("speed_increase", speedIncrease.get()))
    speedIncrease.pack()

    clarifylabel = ctk.CTkLabel(toplevel, text="Difficulty", font=(dependencies.get_font_path(), 12))
    clarifylabel.pack()
    difficultyVal = getSettings("difficulty")
    if not difficultyVal: difficultyVal = "Normal"
    difficultySelector = ctk.CTkSegmentedButton(toplevel, values=["Easy", "Normal", "Hard"], command=lambda v: setSettings("difficulty", v))
    difficultySelector.set(difficultyVal)
    difficultySelector.pack(pady=5)

    clarifylabel = ctk.CTkLabel(toplevel, text="Game Mode", font=(dependencies.get_font_path(), 12))
    clarifylabel.pack()
    gameModeVal = getSettings("game_mode")
    if not gameModeVal: gameModeVal = "Classic"
    gameModeSelector = ctk.CTkSegmentedButton(toplevel, values=["Classic", "Time Attack", "Zen"], command=lambda v: setSettings("game_mode", v))
    gameModeSelector.set(gameModeVal)
    gameModeSelector.pack(pady=5)
    
    resetSettingsButton = ctk.CTkButton(toplevel, text="Reset Settings", command=lambda: reset_settings(), font=(dependencies.get_font_path(), 12))
    resetSettingsButton.pack(pady=10)

    # Audio Settings
    ctk.CTkLabel(toplevel, text="Volume", font=(dependencies.get_font_path(), 12)).pack()
    current_vol = float(getSettings("volume") or 0.5)
    volumeSlider = ctk.CTkSlider(toplevel, from_=0, to=1, command=lambda v: setSettings("volume", str(round(v, 2))))
    volumeSlider.set(current_vol)
    volumeSlider.pack(pady=5)

    mutedVal = getSettings("muted") == "True"
    muteSwitch = ctk.CTkSwitch(toplevel, text="Mute", command=lambda: setSettings("muted", str(muteSwitch.get() == 1)))
    if mutedVal: muteSwitch.select()
    muteSwitch.pack(pady=5)
    
    toplevel.lift()
    toplevel.focus_force()
    modloader.trigger_on_settings(toplevel)
    toplevel.wait_window()


def start(root):
    options(root)
