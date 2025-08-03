import customtkinter as ctk
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
    done_button = ctk.CTkButton(root, text="Save", command=retuna)
    done_button.pack()
    exit_button = ctk.CTkButton(root, text="Exit", command=root.destroy)
    exit_button.pack()
    root.bind('<Return>', lambda event: retuna())
    root.bind('<Escape>', lambda event: root.destroy())
    root.focus_set()
    root.mainloop()
    return retun
