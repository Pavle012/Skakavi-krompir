import importlib.util
import subprocess
import sys
import os


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
    
    folder_path = "./assets"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder '{folder_path}' created.")
    else:
        print(f"Folder '{folder_path}' already exists.")
    
    fetch_assets()
    
    # to be continued

    default_settings_path = "./settings.txt"
    if not os.path.exists(default_settings_path):
        with open(default_settings_path, "w") as f:
            f.write("scrollPixelsPerFrame=8\n")
            f.write("jumpVelocity=8\n")
            f.write("maxFps=60\n")
            f.write("rememberName=False\n")
            f.write("name=User\n")
        print(f"Default settings file '{default_settings_path}' created.")

def fetch_assets():
    import requests
    
    folder_path = "./assets"
    
    assets = {
        "font.ttf": "https://github.com/Pavle012/Skakavi-krompir/raw/refs/heads/main/assets/font.ttf",
        "potato.png": "https://github.com/Pavle012/Skakavi-krompir/raw/refs/heads/main/assets/potato.png",
        "potato.ico": "https://github.com/Pavle012/Skakavi-krompir/raw/refs/heads/main/assets/potato.ico"
    }

    # Download each asset
    for filename, url in assets.items():
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
