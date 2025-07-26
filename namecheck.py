import tkinter as tk
def getname():
    def retuna():
        global retun
        retun = entry.get()
    root = tk.Tk()
    root.title("Enter Your Name")
    label = tk.Label(root, text="Please enter your name:")
    label.pack()
    root.geometry("300x200")
    entry = tk.Entry(root)
    entry.pack()
    done_button = tk.Button(root, text="Save", command=retuna)
    done_button.pack()
    exit_button = tk.Button(root, text="Exit", command=root.destroy)
    exit_button.pack()
    root.bind('<Return>', lambda event: retuna())
    root.bind('<Escape>', lambda event: root.destroy())
    root.focus_set()
    root.mainloop()
    return retun
