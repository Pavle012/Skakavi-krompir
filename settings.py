import tkinter as tk
from tkinter import filedialog
import subprocess


def upload_font():
    file_path = filedialog.askopenfilename(
        initialdir="/",
        title="Select a Font File",
        filetypes=(("Font files", "*.ttf"), ("All files", "*.*"))
    )
    
    if file_path:
        subprocess.run(["cp", file_path, "assets/font.ttf"])

root = tk.Tk()
settingsLabel = tk.Label(root, text="Settings", font=("assets/Poppins.ttf", 24))
settingsLabel.pack()
uploadFontButton = tk.Button(root, text="Upload Font", command=upload_font, font=("assets/Poppins.ttf", 16))
uploadFontButton.pack()


root.title("skakavi krompir settings")
root.geometry("300x200")
root.mainloop()