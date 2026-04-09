from tkinter import simpledialog, filedialog

from utils import update_user_config

def prompt_directory(root, label):
    return filedialog.askdirectory(title=f"Select {label}", parent=root)

def prompt_file(root, label, filetypes):
    return filedialog.askopenfilename(
        title=f"Select {label}",
        parent=root,
        filetypes=filetypes
    )

def prompt_list(root, label):
    return simpledialog.askstring("Set List", f"Enter one or more {label} (separated by |):", parent=root)

def update_and_show(root, config, key, label,
                    ask_dir=False, ask_filetypes=None, is_list=False,
                    refresh_fn=None):
    if ask_dir:
        new_val = prompt_directory(root, label)
    elif ask_filetypes:
        new_val = prompt_file(root, label, ask_filetypes)
    elif is_list:
        new_val = prompt_list(root, label)
        if new_val:
            new_val = [v.strip() for v in new_val.split("|") if v.strip()]
    else:
        new_val = simpledialog.askstring("Update Value", f"Enter new value for {label}:", parent=root)

    if new_val:
        update_user_config(config, key, new_val)
        if refresh_fn:
            refresh_fn()
