from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QPushButton, 
                             QLabel, QWidget, QFileDialog, QLineEdit, QCheckBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont
import scores as scs
import options
import dependencies
import os
import sys

def apply_breeze_dark(app):
    # Try to use the system's "real" Breeze style if it's available in the Qt environment
    from PyQt6.QtWidgets import QStyleFactory
    if "Breeze" in QStyleFactory.keys():
        app.setStyle("Breeze")
        return
    
    # Otherwise, apply a high-fidelity "Real" Breeze Dark replica via QSS
    # This uses the exact KDE Breeze Dark color palette and styling rules
    app.setStyle("Fusion") # Base style for clean inheritance
    
    breeze_dark_qss = """
    /* Main Window and Dialogs */
    QWidget {
        background-color: #232629;
        color: #eff0f1;
        selection-background-color: #3daee9;
        selection-color: #eff0f1;
        font-family: 'Noto Sans', 'Arial';
    }
    
    /* Buttons */
    QPushButton {
        background-color: #31363b;
        color: #eff0f1;
        border: 1px solid #76797c;
        border-radius: 2px;
        padding: 5px 15px;
        min-height: 25px;
    }
    QPushButton:hover {
        border: 1px solid #3daee9;
    }
    QPushButton:pressed {
        background-color: #2a2e32;
        border: 1px solid #3daee9;
    }
    QPushButton:default {
        border-color: #3daee9;
    }
    
    /* Inputs */
    QLineEdit {
        background-color: #1b1e20;
        border: 1px solid #76797c;
        border-radius: 2px;
        padding: 3px;
        color: #eff0f1;
    }
    QLineEdit:focus {
        border: 1px solid #3daee9;
    }
    
    /* Scroll Areas */
    QScrollArea {
        border: 1px solid #76797c;
        background-color: #232629;
    }
    
    /* Checkboxes */
    QCheckBox {
        spacing: 10px;
    }
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border: 1px solid #76797c;
        border-radius: 2px;
    }
    QCheckBox::indicator:unchecked {
        background-color: #31363b;
    }
    QCheckBox::indicator:checked {
        background-color: #31363b;
        image: url(no-resource); /* Fallback */
        border: 1px solid #3daee9;
    }
    QCheckBox::indicator:hover {
        border: 1px solid #3daee9;
    }

    /* Labels */
    QLabel {
        background: transparent;
    }
    """
    app.setStyleSheet(breeze_dark_qss)

def get_common_font(size=16):
    font_path = dependencies.get_font_path()
    # PyQt can load fonts by file path if needed, but here we assume family matching or default
    return QFont("Arial", size) # Fallback to Arial for simplicity in this easy wrapper

class EasyDialog(QDialog):
    def __init__(self, title, size=(340, 300), parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(size[0], size[1])
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.layout)
        
        icon_path = dependencies.get_potato_path()
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
    def add_label(self, text, font_size=24):
        label = QLabel(text)
        label.setFont(get_common_font(font_size))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(label)
        return label
        
    def add_button(self, text, callback, font_size=16):
        btn = QPushButton(text)
        btn.setFont(get_common_font(font_size))
        btn.setFixedSize(200, 40)
        btn.clicked.connect(callback)
        self.layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
        return btn

# --- Core Screens ---

def lose_screen(root_dummy):
    dialog = EasyDialog("skakavi krompir", size=(300, 250))
    dialog.add_label("You lost!", 24)
    
    returncode = "error"

    def restart():
        nonlocal returncode
        returncode = "restart"
        dialog.accept()

    def exit_game():
        nonlocal returncode
        returncode = "exit"
        dialog.reject()

    dialog.add_button("Restart", restart)
    dialog.add_button("Exit", exit_game)
    dialog.add_button("Public Leaderboard", lambda: scs.start_public(None))
    
    dialog.exec()
    return returncode

def main_menu(root_dummy):
    dialog = EasyDialog("skakavi krompir", size=(340, 350))
    dialog.add_label("Skakavi Krompir", 24)
    
    returncode = "exit"

    def start_game():
        nonlocal returncode
        returncode = "start"
        dialog.accept()

    def quit_game():
        nonlocal returncode
        returncode = "exit"
        dialog.reject()

    dialog.add_button("Start Game", start_game)
    dialog.add_button("Settings", lambda: options.start(None))
    dialog.add_button("Scores", lambda: scs.start(None))
    dialog.add_button("Public Leaderboard", lambda: scs.start_public(None))
    dialog.add_button("Exit", quit_game)
    
    dialog.exec()
    return returncode

def pause_screen(root_dummy):
    dialog = EasyDialog("skakavi krompir", size=(340, 400))
    dialog.add_label("Paused", 24)
    
    returncode = "resume"

    def resume():
        nonlocal returncode
        returncode = "resume"
        dialog.accept()

    def exit_game():
        nonlocal returncode
        returncode = "exit"
        dialog.reject()

    dialog.add_button("Scores", lambda: scs.start(None))
    dialog.add_button("Public Leaderboard", lambda: scs.start_public(None))
    dialog.add_button("Resume", resume)
    dialog.add_button("Exit", exit_game)
    dialog.add_button("Settings", lambda: options.start(None))
    
    def update_game():
        import updater
        game_executable_path = sys.argv[0]
        updater.start_update(game_executable_path)
        exit_game()
        
    dialog.add_button("Update", update_game)
    
    dialog.exec()
    return returncode

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