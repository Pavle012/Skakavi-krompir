# if os is linux download updater.sh to tmp and run it
# if os is windows download updater.bat to tmp and run it
import os
import platform
import urllib.request
import subprocess
import tempfile

if platform.system() == "Linux":
    url = "https://raw.githubusercontent.com/Pavle012/Skakavi-krompir/refs/heads/main/updater.sh"
    file_extension = ".sh"
    run_command = ["bash"]
elif platform.system() == "Windows":
    url = "https://raw.githubusercontent.com/Pavle012/Skakavi-krompir/refs/heads/main/updater.bat"
    file_extension = ".bat"
    run_command = []
else:
    raise Exception("Unsupported OS")

temp_dir = tempfile.gettempdir()
file_path = os.path.join(temp_dir, "updater" + file_extension)
urllib.request.urlretrieve(url, file_path)
subprocess.Popen(run_command + [file_path])
