import importlib.util
import subprocess
import sys

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
