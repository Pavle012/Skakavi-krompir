from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import shutil
import dependencies
import os
from PIL import Image
import gui

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

def options(root_dummy):
    dialog = gui.EasyDialog("skakavi krompir settings", size=(400, 500))
    dialog.add_label("Settings", 24)

    def get_val(key, default):
        v = getSettings(key)
        return v if v is not None else str(default)

    def upload_font():
        file_path, _ = QFileDialog.getOpenFileName(dialog, "Select a Font File", "/", "Font files (*.ttf)")
        if file_path:
            shutil.copyfile(file_path, os.path.join(dependencies.get_user_data_dir(), "font.ttf"))

    def upload_potato():
        file_path, _ = QFileDialog.getOpenFileName(dialog, "Select an Image File", "/", "Image files (*.png)")
        if file_path:
            custom_potato_path = os.path.join(dependencies.get_user_data_dir(), "potato.png")
            shutil.copyfile(file_path, custom_potato_path)
            with Image.open(custom_potato_path) as img:
                img.save(os.path.join(dependencies.get_user_data_dir(), "potato.ico"), format='ICO', sizes=[(64, 64)])
            dependencies.load_global_icon_pil()
            dialog.setWindowIcon(QIcon(custom_potato_path))

    dialog.add_button("Upload Font", upload_font)
    dialog.add_button("Upload Potato", upload_potato)

    inputs = {}
    for label_text, key, default in [
        ("Speed", "scrollPixelsPerFrame", 8),
        ("Jump height", "jumpVelocity", 8),
        ("Max FPS", "maxFps", 60),
        ("Speed increase", "speed_increase", 0.03)
    ]:
        dialog.add_label(label_text, 12)
        edit = QLineEdit(get_val(key, default))
        edit.setFont(gui.get_common_font(16))
        dialog.layout.addWidget(edit)
        inputs[key] = edit

    def save():
        for key, edit in inputs.items():
            setSettings(key, edit.text())
        dialog.accept()

    def reset():
        if QMessageBox.question(dialog, "Reset", "Are you sure?") == QMessageBox.StandardButton.Yes:
            data_dir = dependencies.get_user_data_dir()
            if os.path.exists(data_dir):
                shutil.rmtree(data_dir)
            dependencies.load_global_icon_pil()
            dialog.reject()

    dialog.add_button("Save & Exit", save)
    dialog.add_button("Reset", reset)
    dialog.add_button("Cancel", dialog.reject)

    dialog.exec()

def start(root_dummy):
    options(None)