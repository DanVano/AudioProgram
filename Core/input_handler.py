import tkinter as tk
from tkinter import simpledialog, filedialog

from utils import update_user_config

def update_text_result(text_widget, label, value):
    text_widget.insert(tk.END, f"{label}:\n{value}\n\n")

def prompt_directory(root, label):
    return filedialog.askdirectory(title=f"Select {label}", parent=root)

def prompt_file(root, label, filetypes):
    return filedialog.askopenfilename(
        title=f"Select {label}",
        parent=root,
        filetypes=filetypes
    )

def prompt_path(root, label):
    # legacy (string) prompt kept for other uses
    return simpledialog.askstring("Set Path", f"Enter new {label}:", parent=root)

def prompt_list(root, label):
    return simpledialog.askstring("Set List", f"Enter one or more {label} (separated by |):", parent=root)

def update_and_show(root, text_widget, config, key, label, ask_dir=False, ask_filetypes=None, is_list=False):
    if ask_dir:
        new_val = prompt_directory(root, label)
    elif ask_filetypes:
        new_val = prompt_file(root, label, ask_filetypes)
    elif is_list:
        new_val = prompt_list(root, label)
        if new_val:
            new_val = new_val.split("|")
    else:
        new_val = simpledialog.askstring("Update Value", f"Enter new value for {label}:", parent=root)

    if new_val:
        update_user_config(config, key, new_val)
        update_text_result(text_widget, label, config[key])
