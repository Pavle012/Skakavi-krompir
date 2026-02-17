import importlib.util
import subprocess
import sys
import os
import shutil
from PIL import Image, ImageTk # Added ImageTk


global_icon_pil_image = None # Only global PIL Image
custom_data_dir = None


def set_custom_data_dir(path):
    global custom_data_dir
    custom_data_dir = path


def is_compiled():
    """
    Checks if the code is running as a compiled executable
    (by PyInstaller, cx_Freeze, or Nuitka).
    """
    # Check for PyInstaller/cx_Freeze
    is_frozen = getattr(sys, "frozen", False)
    # Check for Nuitka
    is_nuitka = "__compiled__" in globals()
    
    return is_frozen or is_nuitka


def get_global_icon_pil():
    """
    Returns the global PIL Image object for the icon.
    """
    return global_icon_pil_image


def load_global_icon_pil():
    global global_icon_pil_image
    icon_path = get_potato_path() # Use the new function to get the correct potato path
    if os.path.exists(icon_path):
        global_icon_pil_image = Image.open(icon_path)
        # Also generate .ico from .png here for consistency
        ico_path = os.path.join(get_user_data_dir(), "potato.ico")
        if not os.path.exists(ico_path):
            global_icon_pil_image.save(ico_path, format='ICO', sizes=[(256, 256)])
            print(f"Generated {ico_path} from {icon_path}")
    else:
        # Fallback to default if no custom/standard icon is found
        default_icon_path = resource_path("assets/potato.png")
        if os.path.exists(default_icon_path):
            global_icon_pil_image = Image.open(default_icon_path)
        else:
            print(f"Warning: Icon file not found at {default_icon_path}. Application may not display icon.")


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for compiled executables """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    elif is_compiled():
        # For Nuitka and others, the assets are relative to the executable
        base_path = os.path.dirname(sys.executable)
    else:
        # Development mode
        base_path = os.path.abspath(".")
        
    return os.path.join(base_path, relative_path)

def get_assets_dir():
    """Get the absolute path to the assets directory."""
    return resource_path("assets")

def get_user_data_dir():
    """ Get path to user data directory, create it if it doesn't exist """
    app_name = "SkakaviKrompir"
    if custom_data_dir:
        data_dir = custom_data_dir
    elif sys.platform == "win32":
        data_dir = os.path.join(os.environ["APPDATA"], app_name)
    else:
        data_dir = os.path.join(os.path.expanduser("~"), ".local", "share", app_name)
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    return data_dir

def get_potato_path():
    """Get the path to the potato image, preferring the custom one if it exists."""
    custom_potato_path = os.path.join(get_user_data_dir(), "potato.png")
    if os.path.exists(custom_potato_path):
        return custom_potato_path
    return resource_path("assets/potato.png")


def get_font_path():
    """Get the path to the font file, preferring the custom one if it exists."""
    custom_font_path = os.path.join(get_user_data_dir(), "font.ttf")
    if os.path.exists(custom_font_path):
        return custom_font_path
    return resource_path("assets/font.ttf")


def ensure_installed(package_name, import_name=None):
    if is_compiled():
        return
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


def checkifdepend():
    ensure_installed("customtkinter")
    ensure_installed("pygame")
    ensure_installed("pillow", "PIL")
    ensure_installed("requests")


def copy_default_assets():
    """Copy default assets to user data directory if they don't exist."""
    user_data_dir = get_user_data_dir()
    assets = ["potato.png", "font.ttf"]
    for asset in assets:
        dest_path = os.path.join(user_data_dir, asset)
        if not os.path.exists(dest_path):
            src_path = resource_path(os.path.join("assets", asset))
            if os.path.exists(src_path):
                shutil.copy(src_path, dest_path)
                print(f"Copied {asset} to user data directory.")

def install_configs():
    # install all assets and default settings
    copy_default_assets()
    default_settings_path = os.path.join(get_user_data_dir(), "settings.txt")
    if not os.path.exists(default_settings_path):
        with open(default_settings_path, "w") as f:
            f.write("scrollPixelsPerFrame=8\n")
            f.write("jumpVelocity=8\n")
            f.write("maxFps=60\n")
            f.write("rememberName=False\n")
            f.write("name=User\n")
            f.write("speed_increase=0.03\n")
        print(f"Default settings file '{default_settings_path}' created.")
    create_shortcut()

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

def create_shortcut():
    """
    Creates a desktop shortcut for the application if it is running as a compiled executable.
    """
    if is_compiled():
        if sys.platform == "win32":
            try:
                import winshell
                from win32com.client import Dispatch
            except ModuleNotFoundError:
                print("Could not create shortcut: winshell or pywin32 not found.")
                print("Please install them with: pip install winshell pywin32")
                return

            app_name = "Skakavi Krompir"
            app_path = sys.executable  # Use sys.executable for the compiled app path
            icon_path = os.path.join(get_user_data_dir(), "potato.ico")
            
            # Create a shortcut in the start menu
            start_menu = winshell.start_menu()
            shortcut_path = os.path.join(start_menu, f"{app_name}.lnk")
            
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)

            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = app_path
            shortcut.WorkingDirectory = os.path.dirname(app_path)
            shortcut.IconLocation = icon_path
            shortcut.save()
            print(f"Created shortcut at {shortcut_path}")


    else:
        print("Application not compiled. Skipping shortcut creation.")
