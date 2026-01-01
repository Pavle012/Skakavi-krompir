from PyQt6.QtWidgets import QLineEdit, QCheckBox
import dependencies
import os
import gui

retun = "Unnamed"

def getname(root_dummy):
    global retun
    dialog = gui.EasyDialog("Enter Your Name", size=(300, 200))
    dialog.add_label("Your Name:", 16)
    
    edit = QLineEdit()
    edit.setFont(gui.get_common_font(12))
    dialog.layout.addWidget(edit)
    
    check = QCheckBox("Remember name")
    check.setFont(gui.get_common_font(12))
    dialog.layout.addWidget(check)

    def save():
        global retun
        retun = edit.text()
        
        def setSettings(key, newValue):
            settings = {}
            settings_path = os.path.join(dependencies.get_user_data_dir(), "settings.txt")
            if os.path.exists(settings_path):
                with open(settings_path) as f:
                    for line in f:
                        if "=" in line:
                            k, value = line.strip().split("=", 1)
                            settings[k] = value
            settings[key] = newValue
            with open(settings_path, "w") as f:
                for k, value in settings.items():
                    f.write(f"{k}={value}\n")

        if check.isChecked():
            setSettings("rememberName", "True")
            setSettings("name", retun)
        else:
            setSettings("rememberName", "False")
        
        dialog.accept()

    dialog.add_button("Save", save)
    dialog.add_button("Exit", dialog.reject)

    dialog.exec()
    return retun
