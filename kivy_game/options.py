"""
options.py — Settings screen rendered natively in Kivy.
Maintains the same settings_defs structure as the original Pygame version
but uses Kivy widgets (ScrollView, Slider, Spinner) to display them.
"""

import shutil
import os
import sys
from shared import modloader
from shared import dependencies

from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.core.window import Window

# File chooser is only available on non-Android platforms
if sys.platform != "android":
    from plyer import filechooser

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
    try:
        path = filechooser.open_file(title="Select a Font File", filters=[("Font files", "*.ttf")])
        if path and path[0]:
            shutil.copyfile(path[0], os.path.join(dependencies.get_user_data_dir(), "font.ttf"))
            print(f"Font uploaded from {path[0]}")
    except Exception as e:
        print(f"File picker error: {e}")

def _upload_image(current_values):
    try:
        path = filechooser.open_file(title="Select Potato Image (PNG)", filters=[("Transparent PNG", "*.png")])
        if path and path[0]:
            from PIL import Image
            custom_potato_path = os.path.join(dependencies.get_user_data_dir(), "potato.png")
            custom_ico_path = os.path.join(dependencies.get_user_data_dir(), "potato.ico")
            shutil.copyfile(path[0], custom_potato_path)
            with Image.open(custom_potato_path) as img:
                img.save(custom_ico_path, format="ICO", sizes=[(64, 64)])
            dependencies.load_global_icon_pil()
            print(f"Potato image uploaded from {path[0]}")
    except Exception as e:
        print(f"File picker error: {e}")

def _upload_sound(sound_type):
    try:
        path = filechooser.open_file(title=f"Select {sound_type.capitalize()} Sound File", filters=[("Audio files", "*.wav", "*.mp3")])
        if path and path[0]:
            ext = os.path.splitext(path[0])[1]
            dest_folder = dependencies.get_assets_dir()
            for old_ext in (".wav", ".mp3"):
                old = os.path.join(dest_folder, f"{sound_type}{old_ext}")
                if os.path.exists(old):
                    os.remove(old)
            dest_path = os.path.join(dest_folder, f"{sound_type}{ext}")
            shutil.copyfile(path[0], dest_path)
            print(f"Uploaded {sound_type} to {dest_path}")
    except Exception as e:
        print(f"File picker error: {e}")

def _reset_settings(current_values):
    data_dir = dependencies.get_user_data_dir()
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)
    dependencies.load_global_icon_pil()
    print("Settings reset.")
    return "__reset__"


class SettingsModal(ModalView):
    def __init__(self, current_values, settings_defs, on_close, **kwargs):
        super().__init__(**kwargs)
        self.current_values = current_values
        self.settings_defs = settings_defs
        self.on_close_callback = on_close
        
        self.background_color = [0, 0, 0, 150/255.0]
        self.size_hint = (0.8, 0.9)
        self.auto_dismiss = False

        with self.canvas.before:
            Color(30/255, 30/255, 40/255, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
            Color(1, 1, 1, 1)
            self.line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 20), width=2)
            
        self.bind(pos=self.update_graphics, size=self.update_graphics)
        
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        title = Label(text="Settings", font_size=48, bold=True, size_hint_y=None, height=60)
        main_layout.add_widget(title)
        
        scroll = ScrollView(size_hint_y=1)
        grid = GridLayout(cols=2, spacing=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        for idx, def_item in enumerate(settings_defs):
            t = def_item["type"]
            if t == "section":
                grid.add_widget(Label(text=f"[b]{def_item['label']}[/b]", markup=True, font_size=32, size_hint_y=None, height=50, halign="left", color=(155/255, 89/255, 182/255, 1)))
                grid.add_widget(Label(size_hint_y=None, height=50))
            elif t in ["int", "slider"]:
                key = def_item["key"]
                val = float(self.current_values.get(key, def_item.get("default", 0)))
                
                grid.add_widget(Label(text=def_item["label"], font_size=24, size_hint_y=None, height=50, halign="right"))
                
                box = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
                sl = Slider(min=def_item["min"], max=def_item["max"], value=val, step=def_item.get("step", 0.01))
                val_lbl = Label(text=str(round(val, 2)), size_hint_x=None, width=50)
                
                def make_slider_cb(k, lbl, is_int):
                    def cb(instance, value):
                        v = int(value) if is_int else round(value, 2)
                        lbl.text = str(v)
                        self.current_values[k] = str(v)
                    return cb
                    
                sl.bind(value=make_slider_cb(key, val_lbl, t == "int"))
                box.add_widget(sl)
                box.add_widget(val_lbl)
                grid.add_widget(box)
                
            elif t == "select":
                key = def_item["key"]
                val = self.current_values.get(key, def_item["options"][0])
                
                grid.add_widget(Label(text=def_item["label"], font_size=24, size_hint_y=None, height=50, halign="right"))
                
                sp = Spinner(text=val, values=def_item["options"], size_hint_y=None, height=45)
                def make_spinner_cb(k):
                    def cb(spinner, text):
                        self.current_values[k] = text
                    return cb
                sp.bind(text=make_spinner_cb(key))
                grid.add_widget(sp)
                
            elif t == "bool":
                key = def_item["key"]
                val = self.current_values.get(key, "False") == "True"
                
                grid.add_widget(Label(text=def_item["label"], font_size=24, size_hint_y=None, height=50, halign="right"))
                btn = Button(text="ON" if val else "OFF", size_hint_y=None, height=45, background_color=(0,1,0,1) if val else (1,0,0,1))
                def make_bool_cb(k, b):
                    def cb(instance):
                        v = self.current_values.get(k, "False") == "True"
                        new_v = not v
                        self.current_values[k] = str(new_v)
                        b.text = "ON" if new_v else "OFF"
                        b.background_color = (0,1,0,1) if new_v else (1,0,0,1)
                    return cb
                btn.bind(on_release=make_bool_cb(key, btn))
                grid.add_widget(btn)
                
            elif t == "action":
                grid.add_widget(Label(text=def_item["label"], font_size=24, size_hint_y=None, height=50, halign="right"))
                btn = Button(text=def_item.get("btn_label", "Action"), size_hint_y=None, height=45)
                # Keep a reference to action to avoid late binding issues
                def make_action_cb(act):
                    def cb(instance):
                        res = act()
                        if res == "__reset__":
                            self.current_values["__reset__"] = True
                    return cb
                btn.bind(on_release=make_action_cb(def_item["action"]))
                grid.add_widget(btn)

        scroll.add_widget(grid)
        main_layout.add_widget(scroll)
        
        # Save & Close Button
        btn_close = Button(text="Save & Close", size_hint=(None, None), size=(200, 50), pos_hint={'center_x': 0.5}, background_color=(46/255, 204/255, 113/255, 1))
        btn_close.bind(on_release=self.close_modal)
        main_layout.add_widget(btn_close)
        
        self.add_widget(main_layout)

    def update_graphics(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.line.rounded_rectangle = (self.x, self.y, self.width, self.height, 20)
        
    def close_modal(self, instance):
        if self.on_close_callback:
            self.on_close_callback(self.current_values)
        self.dismiss()

def start_settings(on_close=None):
    current_values = _get_settings()
    
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

    def do_reset():
        return _reset_settings(current_values)

    settings_defs = [
        {"type": "section", "label": "Gameplay"},
        {"type": "int", "key": "scrollPixelsPerFrame", "label": "Speed", "min": 1, "max": 20, "step": 1, "default": 2},
        {"type": "int", "key": "jumpVelocity", "label": "Jump Height", "min": 1, "max": 30, "step": 1, "default": 12},
        {"type": "int", "key": "speed_increase", "label": "Speed Increase", "min": 0, "max": 20, "step": 1, "default": 3},
        {"type": "select", "key": "difficulty", "label": "Difficulty", "options": ["Easy", "Normal", "Hard"]},
        {"type": "select", "key": "game_mode", "label": "Game Mode", "options": ["Classic", "Time Attack", "Zen"]},
        {"type": "section", "label": "Display & Performance"},
        {"type": "int", "key": "maxFps", "label": "Max FPS", "min": 10, "max": 240, "step": 10, "default": 60},
        {"type": "section", "label": "Audio"},
        {"type": "slider", "key": "volume", "label": "Volume", "min": 0.0, "max": 1.0},
        {"type": "bool", "key": "muted", "label": "Muted"},
    ]
    
    # Only add custom asset upload options on non-Android platforms
    if sys.platform != "android":
        settings_defs.extend([
            {"type": "section", "label": "Custom Assets"},
            {"type": "action", "label": "Upload Font", "btn_label": "Browse…", "action": _upload_font},
            {"type": "action", "label": "Upload Potato Image", "btn_label": "Browse…", "action": lambda: _upload_image(current_values)},
            {"type": "action", "label": "Upload Jump Sound", "btn_label": "Browse…", "action": lambda: _upload_sound("jump")},
            {"type": "action", "label": "Upload Death Sound", "btn_label": "Browse…", "action": lambda: _upload_sound("death")},
            {"type": "action", "label": "Upload Score Sound", "btn_label": "Browse…", "action": lambda: _upload_sound("score")},
            {"type": "action", "label": "Upload Powerup Sound", "btn_label": "Browse…", "action": lambda: _upload_sound("powerup")},
            {"type": "action", "label": "Upload Music", "btn_label": "Browse…", "action": lambda: _upload_sound("music")},
        ])
    
    settings_defs.append({"type": "section", "label": "Danger Zone"})
    settings_defs.append({"type": "action", "label": "Reset All Settings", "btn_label": "Reset", "action": do_reset})

    modloader.trigger_on_settings(settings_defs)

    def hook_close(updated_vals):
        if updated_vals.pop("__reset__", False):
            dependencies.install_configs()
        else:
            _save_settings(updated_vals)
        if on_close:
            on_close()

    modal = SettingsModal(current_values, settings_defs, hook_close)
    modal.open()
