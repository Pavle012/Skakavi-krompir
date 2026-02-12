import customtkinter as ctk
import scores as scs
import modloader
import options
import dependencies
from PIL import Image, ImageTk
import os
import replays
returncode = "error"

# lose_screen has been moved to main.py using Pygame


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

def main_menu(root):
    global returncode
    toplevel = ctk.CTkToplevel(root)
    toplevel.title("skakavi krompir")
    toplevel.geometry("340x300")

    def exit_game():
        global returncode
        returncode = "exit"
        toplevel.destroy()

    def start_game():
        global returncode
        returncode = "start"
        toplevel.destroy()

    def settings():
        options.start(root)

    def scores():
        scs.start(root)

    def show_replays():
        global returncode
        replay_data = replays.start(root)
        if replay_data:
            returncode = ("replay", replay_data)
            toplevel.destroy()

    # Use the globally loaded icon
    pil_icon = dependencies.get_global_icon_pil()
    if pil_icon:
        icon_photo = ImageTk.PhotoImage(pil_icon)
        toplevel._icon_photo_ref = icon_photo # Keep a strong reference
        toplevel.iconphoto(True, icon_photo)
    
    mainlabel = ctk.CTkLabel(toplevel, text="Skakavi Krompir", font=(dependencies.get_font_path(), 24))
    mainlabel.pack(pady=10)

    startButton = ctk.CTkButton(toplevel, text="Start Game", command=start_game, font=(dependencies.get_font_path(), 16))
    startButton.pack(pady=5)

    settingsButton = ctk.CTkButton(toplevel, text="Settings", command=settings, font=(dependencies.get_font_path(), 16))
    settingsButton.pack(pady=5)

    scoresButton = ctk.CTkButton(toplevel, text="Scores", command=scores, font=(dependencies.get_font_path(), 16))
    scoresButton.pack(pady=5)

    publicScoresButton = ctk.CTkButton(toplevel, text="Public Leaderboard", command=lambda: scs.start_public(root), font=(dependencies.get_font_path(), 16))
    publicScoresButton.pack(pady=5)

    replaysButton = ctk.CTkButton(toplevel, text="Replays", command=show_replays, font=(dependencies.get_font_path(), 16))
    replaysButton.pack(pady=5)
    
    exitButton = ctk.CTkButton(toplevel, text="Exit", command=exit_game, font=(dependencies.get_font_path(), 16))
    exitButton.pack(pady=5)
    
    toplevel.protocol("WM_DELETE_WINDOW", exit_game)
    modloader.trigger_on_main_menu(toplevel)
    toplevel.wait_window()
    return returncode




def pause_screen(root):
    global returncode
    toplevel = ctk.CTkToplevel(root)
    toplevel.title("skakavi krompir")
    toplevel.geometry("340x300")
    
    def exit_game():
        global returncode
        returncode = "exit"
        toplevel.destroy()
    def resume():
        global returncode
        returncode = "resume"
        toplevel.destroy()
    def settings():
        options.start(root)
    def scores():
        scs.start(root)
    def update():
        import updater
        import sys
        game_executable_path = sys.argv[0]
        updater.start_update(game_executable_path)
        exit_game()
    
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
    public_leaderboard_button = ctk.CTkButton(toplevel, text="Public Leaderboard", command=lambda: scs.start_public(root), font=(dependencies.get_font_path(), 16))
    resumebutton = ctk.CTkButton(toplevel, text="Resume", command=resume, font=(dependencies.get_font_path(), 16))
    exitbutton = ctk.CTkButton(toplevel, text="Exit", command=exit_game, font=(dependencies.get_font_path(), 16))
    settingsbutton = ctk.CTkButton(toplevel, text="Settings", command=settings, font=(dependencies.get_font_path(), 16))
    updatebutton = ctk.CTkButton(toplevel, text="Update", command=update, font=(dependencies.get_font_path(), 16))
    scorebutton.pack()
    public_leaderboard_button.pack()
    resumebutton.pack()
    exitbutton.pack()
    settingsbutton.pack()
    updatebutton.pack()

    modloader.trigger_on_pause_screen(toplevel)
    toplevel.wait_window()
    return returncode
