import customtkinter as ctk
retun = "Unnamed"
def getname():
    def retuna():
        global retun
        retun = entry.get()
    root = ctk.CTk()
    root.iconbitmap("assets/potato.ico")
    root.title("Enter Your Name")
    label = ctk.CTkLabel(root, text="Please enter your name:")
    label.pack()
    root.geometry("300x200")
    entry = ctk.CTkEntry(root)
    entry.pack()
    rememberCheck = ctk.CTkCheckBox(root, text="Remember name")
    rememberCheck.pack()
    done_button = ctk.CTkButton(root, text="Save", command=retuna)
    done_button.pack()
    exit_button = ctk.CTkButton(root, text="Exit", command=root.destroy)
    exit_button.pack()
    root.bind('<Return>', lambda event: retuna())
    root.bind('<Escape>', lambda event: root.destroy())
    root.focus_set()
    root.mainloop()

    def setSettings(key, newValue):
        settings = {}
        with open("settings.txt") as f:
            for line in f:
                if "=" in line:
                    k, value = line.strip().split("=", 1)
                    settings[k] = value
        settings[key] = newValue
        with open("settings.txt", "w") as f:
            for k, value in settings.items():
                f.write(f"{k}={value}\n")
    
    if rememberCheck.get():
        setSettings("rememberName", True)
        setSettings("name", retun)
    else:
        setSettings("rememberName", False)
    
    return retun
