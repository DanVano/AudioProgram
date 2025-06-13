import tkinter as tk
from tkinter import simpledialog
from utils import update_user_config

def update_text_result(text_widget, label, value):
    text_widget.insert(tk.END, f"{label}:\n{value}\n\n")

def prompt_path(root, label):
    return simpledialog.askstring("Set Path", f"Enter new {label}:", parent=root)

def prompt_list(root, label):
    return simpledialog.askstring("Set List", f"Enter one or more {label} (separated by |):", parent=root)

def update_and_show(root, text_widget, config, key, label, ask_path=False, is_list=False):
    if ask_path:
        new_val = prompt_path(root, label)
    elif is_list:
        new_val = prompt_list(root, label)
        if new_val:
            new_val = new_val.split("|")
    else:
        new_val = simpledialog.askstring("Update Value", f"Enter new value for {label}:", parent=root)

    if new_val:
        update_user_config(config, key, new_val)
        update_text_result(text_widget, label, config[key])
