import os
import platform
import urllib.request
import subprocess
import tempfile
import sys
from subprocess import DEVNULL

def start_update(game_executable_path):
    """
    Downloads and runs the appropriate updater script (.sh or .bat) for the current OS.

    The updater script is responsible for downloading and installing the latest
    version of the game. This function passes the path of the current game
    executable to the script.

    NOTE: This function downloads the updater scripts from the 'main' branch on GitHub.
    Ensure the latest versions of 'updater.sh' and 'updater.bat' are pushed there.

    Args:
        game_executable_path (str): The absolute path to the game executable to be replaced.
    """
    popen_kwargs = {}
    if platform.system() == "Linux":
        url = "https://raw.githubusercontent.com/Pavle012/Skakavi-krompir/main/updater.sh"
        file_extension = ".sh"
        run_command = ["bash"]
        popen_kwargs = {
            "stdin": DEVNULL,
            "stdout": DEVNULL,
            "stderr": DEVNULL,
            "preexec_fn": os.setsid,
        }
    elif platform.system() == "Windows":
        # Assuming updater.bat exists and works similarly to updater.sh
        url = "https://raw.githubusercontent.com/Pavle012/Skakavi-krompir/main/updater.bat"
        file_extension = ".bat"
        run_command = []  # .bat files can often be executed directly
    else:
        print(f"Updater not supported for OS: {platform.system()}", file=sys.stderr)
        return

    # Ensure the provided path is absolute
    if not os.path.isabs(game_executable_path):
        game_executable_path = os.path.abspath(game_executable_path)

    try:
        temp_dir = tempfile.gettempdir()
        script_path = os.path.join(temp_dir, "updater" + file_extension)

        print(f"Downloading updater script from {url}...")
        urllib.request.urlretrieve(url, script_path)
        print(f"Saved to {script_path}")

        # Make the script executable on POSIX systems
        if os.name == 'posix':
            os.chmod(script_path, 0o755)

        command = run_command + [script_path, game_executable_path]
        print(f"Running updater command: {' '.join(command)}")

        # Use Popen to run the updater in a new, independent process.
        # This allows the main application to exit while the updater continues.
        subprocess.Popen(command, **popen_kwargs)

    except Exception as e:
        print(f"An error occurred during the update process: {e}", file=sys.stderr)

if __name__ == '__main__':
    # This block allows the script to be run directly for testing.
    # It expects the path to the game executable as a command-line argument.
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <path_to_game_executable>")
        sys.exit(1)

    game_path_arg = sys.argv[1]
    print(f"Starting update for executable: {game_path_arg}")
    start_update(game_path_arg)
    print("Updater process has been launched.")
    # In a real scenario, the main application would now exit.
    # e.g., sys.exit(0)
