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
