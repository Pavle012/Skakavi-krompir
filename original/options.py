"""
options.py  —  Settings screen rendered as a pygame overlay.
Uses hidden tkinter (standard library) only for file-picker dialogs.
No customtkinter required.
"""

import shutil
import os
from shared import modloader
from shared import dependencies
from original import pygame_ui
from PIL import Image


def _get_settings():
    settings = {}
    settings_path = os.path.join(dependencies.get_user_data_dir(), "settings.txt")
    if not os.path.exists(settings_path):
        return settings
    with open(settings_path) as f:
        for line in f:
            if "=" in line:
                k, value = line.strip().split("=", 1)
                settings[k] = value
    return settings


def _save_settings(settings):
    settings_path = os.path.join(dependencies.get_user_data_dir(), "settings.txt")
    with open(settings_path, "w") as f:
        for k, v in settings.items():
            f.write(f"{k}={v}\n")


# ---------- upload helpers ----------

def _upload_font():
    path = pygame_ui.pick_file(
        title="Select a Font File",
        filetypes=(("Font files", "*.ttf"), ("All files", "*.*")),
    )
    if path:
        shutil.copyfile(path, os.path.join(dependencies.get_user_data_dir(), "font.ttf"))
        print(f"Font uploaded from {path}")


def _upload_image(current_values):
    path = pygame_ui.pick_file(
        title="Select Potato Image (PNG)",
        filetypes=(("Transparent PNG", "*.png"), ("All files", "*.*")),
    )
    if path:
        custom_potato_path = os.path.join(dependencies.get_user_data_dir(), "potato.png")
        custom_ico_path = os.path.join(dependencies.get_user_data_dir(), "potato.ico")
        shutil.copyfile(path, custom_potato_path)
        with Image.open(custom_potato_path) as img:
            img.save(custom_ico_path, format="ICO", sizes=[(64, 64)])
        dependencies.load_global_icon_pil()
        print(f"Potato image uploaded from {path}")


def _upload_sound(sound_type):
    path = pygame_ui.pick_file(
        title=f"Select {sound_type.capitalize()} Sound File",
        filetypes=(("Audio files", "*.wav *.mp3"), ("All files", "*.*")),
    )
    if path:
        ext = os.path.splitext(path)[1]
        dest_folder = dependencies.get_assets_dir()
        # Remove old files of either extension
        for old_ext in (".wav", ".mp3"):
            old = os.path.join(dest_folder, f"{sound_type}{old_ext}")
            if os.path.exists(old):
                os.remove(old)
        dest_path = os.path.join(dest_folder, f"{sound_type}{ext}")
        shutil.copyfile(path, dest_path)
        print(f"Uploaded {sound_type} to {dest_path}")


def _reset_settings(current_values):
    data_dir = dependencies.get_user_data_dir()
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)
    dependencies.load_global_icon_pil()
    print("Settings reset.")
    # Signal the caller to reload
    return "__reset__"


# ---------- main entry ----------

def start():
    current_values = _get_settings()

    # Ensure defaults for any missing keys
    defaults = {
        "scrollPixelsPerFrame": "2",
        "jumpVelocity": "12",
        "maxFps": "60",
        "speed_increase": "3",
        "difficulty": "Normal",
        "game_mode": "Classic",
        "volume": "0.5",
        "muted": "False",
    }
    for k, v in defaults.items():
        current_values.setdefault(k, v)

    reset_result = [None]

    def do_reset():
        result = _reset_settings(current_values)
        reset_result[0] = result

    settings_defs = [
        {"type": "section", "label": "Gameplay"},
        {
            "type": "int",
            "key": "scrollPixelsPerFrame",
            "label": "Speed",
            "min": 1,
            "max": 20,
            "step": 1,
            "default": 2,
        },
        {
            "type": "int",
            "key": "jumpVelocity",
            "label": "Jump Height",
            "min": 1,
            "max": 30,
            "step": 1,
            "default": 12,
        },
        {
            "type": "int",
            "key": "speed_increase",
            "label": "Speed Increase",
            "min": 0,
            "max": 20,
            "step": 1,
            "default": 3,
        },
        {
            "type": "select",
            "key": "difficulty",
            "label": "Difficulty",
            "options": ["Easy", "Normal", "Hard"],
        },
        {
            "type": "select",
            "key": "game_mode",
            "label": "Game Mode",
            "options": ["Classic", "Time Attack", "Zen"],
        },
        {"type": "section", "label": "Display & Performance"},
        {
            "type": "int",
            "key": "maxFps",
            "label": "Max FPS",
            "min": 10,
            "max": 240,
            "step": 10,
            "default": 60,
        },
        {"type": "section", "label": "Audio"},
        {
            "type": "slider",
            "key": "volume",
            "label": "Volume",
            "min": 0.0,
            "max": 1.0,
        },
        {
            "type": "bool",
            "key": "muted",
            "label": "Muted",
        },
        {"type": "section", "label": "Custom Assets"},
        {
            "type": "action",
            "label": "Upload Font",
            "btn_label": "Browse…",
            "action": _upload_font,
        },
        {
            "type": "action",
            "label": "Upload Potato Image",
            "btn_label": "Browse…",
            "action": lambda: _upload_image(current_values),
        },
        {
            "type": "action",
            "label": "Upload Jump Sound",
            "btn_label": "Browse…",
            "action": lambda: _upload_sound("jump"),
        },
        {
            "type": "action",
            "label": "Upload Death Sound",
            "btn_label": "Browse…",
            "action": lambda: _upload_sound("death"),
        },
        {
            "type": "action",
            "label": "Upload Score Sound",
            "btn_label": "Browse…",
            "action": lambda: _upload_sound("score"),
        },
        {
            "type": "action",
            "label": "Upload Powerup Sound",
            "btn_label": "Browse…",
            "action": lambda: _upload_sound("powerup"),
        },
        {
            "type": "action",
            "label": "Upload Music",
            "btn_label": "Browse…",
            "action": lambda: _upload_sound("music"),
        },
        {"type": "section", "label": "Danger Zone"},
        {
            "type": "action",
            "label": "Reset All Settings",
            "btn_label": "Reset",
            "action": do_reset,
        },
    ]

    # Allow modloader to add custom settings rows if it wants
    modloader.trigger_on_settings(settings_defs)

    updated = pygame_ui.draw_settings_screen(settings_defs, current_values)

    # Save whatever we got back (even if reset was pressed the dir was wiped)
    if reset_result[0] != "__reset__":
        _save_settings(updated)
    else:
        # Re-install defaults after reset
        dependencies.install_configs()
