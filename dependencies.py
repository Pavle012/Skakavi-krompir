import importlib.util
import subprocess
import sys
import os
from PIL import Image, ImageTk # Added ImageTk


global_icon_pil_image = None # Only global PIL Image


def get_global_icon_photo_if_available():
    if global_icon_pil_image is not None:
        try:
            # Always create a new PhotoImage instance
            return ImageTk.PhotoImage(global_icon_pil_image)
        except RuntimeError as e:
            print(f"DEBUG: Could not create PhotoImage (Tkinter root not yet available): {e}")
            return None # Ensure it's None if creation fails
        except Exception as e:
            print(f"Error creating PhotoImage: {e}")
            return None
    return None


def load_global_icon_pil():
    global global_icon_pil_image
    icon_path = resource_path("assets/potato.png")
    if os.path.exists(icon_path):
        global_icon_pil_image = Image.open(icon_path)
        # Also generate .ico from .png here for consistency
        ico_path = resource_path("assets/potato.ico")
        if not os.path.exists(ico_path):
            global_icon_pil_image.save(ico_path, format='ICO', sizes=[(256, 256)])
            print(f"Generated {ico_path} from {icon_path}")
    else:
        print(f"Warning: Icon file not found at {icon_path}. Application may not display icon.")


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def get_user_data_dir():
    """ Get path to user data directory, create it if it doesn't exist """
    app_name = "SkakaviKrompir"
    if sys.platform == "win32":
        data_dir = os.path.join(os.environ["APPDATA"], app_name)
    else:
        data_dir = os.path.join(os.path.expanduser("~"), ".local", "share", app_name)
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    return data_dir


def checkifdepend():
    def ensure_installed(package_name, import_name=None):
        import_name = import_name or package_name
        try:
            if importlib.util.find_spec(import_name) is None:
                print(f"Installing {package_name}...", flush=True)
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", package_name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.STDOUT
                )
                print(f"{package_name} installed successfully.", flush=True)
            else:
                print(f"{package_name} is already installed.", flush=True)
        except Exception as e:
            print(f"Error checking/installing {package_name}: {e}", flush=True)

    ensure_installed("customtkinter")
    ensure_installed("pygame")
    ensure_installed("pillow", "PIL")
    ensure_installed("requests")


def install_configs():
    # install all assets and default settings
    
    default_settings_path = os.path.join(get_user_data_dir(), "settings.txt")
    if not os.path.exists(default_settings_path):
        with open(default_settings_path, "w") as f:
            f.write("scrollPixelsPerFrame=8\n")
            f.write("jumpVelocity=8\n")
            f.write("maxFps=60\n")
            f.write("rememberName=False\n")
            f.write("name=User\n")
        print(f"Default settings file '{default_settings_path}' created.")

def generate_icon():
    assets_dir = 'assets'
    img_path = os.path.join(assets_dir, 'potato.png')
    ico_path = os.path.join(assets_dir, 'potato.ico')

    if os.path.exists(img_path):
        img = Image.open(img_path)
        img.save(ico_path, format='ICO', sizes=[(256, 256)])
        print(f"Generated {ico_path} from {img_path}")
    else:
        print(f"Error: {img_path} not found.")

def fetch_assets():
    import requests
    
    folder_path = "./assets"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    assets = {
        "font.ttf": "https://github.com/Pavle012/Skakavi-krompir/raw/refs/heads/main/assets/font.ttf",
        "potato.png": "https://github.com/Pavle012/Skakavi-krompir/raw/refs/heads/main/assets/potato.png"
    }

    # Download each asset
    for filename, url in assets.items():
        # only download if they dont exist
        if os.path.exists(os.path.join(folder_path, filename)):
            continue
        try:
            response = requests.get(url)
            response.raise_for_status()  # Check for HTTP errors

            file_path = os.path.join(folder_path, filename)

            # Write the file to the assets directory
            with open(file_path, "wb") as file:
                file.write(response.content)

            print(f"Downloaded: {filename}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {filename} from {url}: {e}")
            
    generate_icon()
