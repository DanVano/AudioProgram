import threading
import tkinter as tk

from tkinter import ttk
from datetime import datetime

from input_handler import update_and_show
from tag_cleaner import run_cleaner
from utils import read_user_config

try:
    from downloader import run_downloader  # may raise RuntimeError if no key
    DOWNLOADER_AVAILABLE = True
    DOWNLOADER_MSG = "Downloader: Ready"
except RuntimeError as e:
    DOWNLOADER_AVAILABLE = False
    DOWNLOADER_MSG = f"Downloader: Disabled — {e}"
    
##print_tag_list

# --- Load config
config = read_user_config()
try:
    last_scanned_date = datetime.strptime(config["last_scanned_date"], "%Y-%m-%dT%H:%M:%S")
except ValueError:
    last_scanned_date = datetime.min

# === GUI Setup ===
root = tk.Tk()
root.title("Audio Program v8.0")
root.configure(bg="#242424")

header = tk.Label(
    root,
    text="MP3 Downloader and Filename Cleaner",
    font=("Segoe UI", 20, "bold"),
    bg="#242424",
    fg="#F8F8F8"
)
header.pack(pady=(12, 6))

text_output = tk.Text(
    root,
    height=20,
    width=90,
    bg="#242424",
    fg="#F8F8F8",
    insertbackground="#F8F8F8",
    highlightbackground="#333",
    highlightcolor="#444",
    padx=16,
    pady=10,
    font=("Segoe UI", 12)
)
text_output.pack(padx=16, pady=6)

# --- Tag configs ---
text_output.tag_configure("bold", font=("Segoe UI", 12, "bold"))
text_output.tag_configure("dotted", foreground="#AAAAAA", spacing1=7, spacing3=2)
text_output.tag_configure("logtitle", font=("Segoe UI", 12, "bold"), spacing1=2)

# --------- Custom Progress Bar Style ---------
style = ttk.Style()
style.theme_use('default')
style.configure(
    "Custom.Horizontal.TProgressbar",
    troughcolor="#444444",   # Mid-grey trough
    background="#d6d6d6",    # Light grey fill
    bordercolor="#555555",
    thickness=18
)
progress = ttk.Progressbar(
    root,
    orient="horizontal",
    length=400,
    mode="determinate",
    style="Custom.Horizontal.TProgressbar"
)
progress.pack(pady=6)

def print_output(msg):
    def _append():
        text_output.insert(tk.END, msg + "\n")
        text_output.see(tk.END)
    root.after(0, _append)

def print_config_with_line():
    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, "Current Config:\n", "bold")
    text_output.insert(tk.END, "   - "); text_output.insert(tk.END, "Music Folder", "bold")
    text_output.insert(tk.END, f":   {config.get('music_folder', '[Not Set]')}\n")
    text_output.insert(tk.END, "   - "); text_output.insert(tk.END, "CSV", "bold")
    text_output.insert(tk.END, f":   {config.get('csv_path', '[Not Set]')}\n")
    text_output.insert(tk.END, "   - "); text_output.insert(tk.END, "Song Tags", "bold")
    text_output.insert(tk.END, f":   {', '.join(config.get('song_tags', []))}\n")
    text_output.insert(tk.END, "   - "); text_output.insert(tk.END, "Website Tags", "bold")
    text_output.insert(tk.END, f":   {', '.join(config.get('web_tags', []))}\n")
    text_output.insert(tk.END, "   - "); text_output.insert(tk.END, "Last Scanned", "bold")
    text_output.insert(tk.END, f":   {config.get('last_scanned_date', '[Not Set]')}\n")
    text_output.insert(tk.END, "   - "); text_output.insert(tk.END, "Downloader Status", "bold")
    text_output.insert(tk.END, f":   {DOWNLOADER_MSG}\n", "bold")
    text_output.insert(tk.END, ". . " * 58 + "\n", "dotted")
    text_output.insert(tk.END, "Operational Log:\n", "logtitle")

# ========== MENU ==========

def on_enter(event):
    event.widget['bg'] = '#555555'  # Lighter grey on hover

def on_leave(event):
    event.widget['bg'] = '#333'     # Restore original

def menu_wrapper(target_fn):
    def wrapped(*args, **kwargs):
        target_fn(*args, **kwargs)
    return wrapped

menu_items = [
    (" 1. Run Shazam Downloader ", lambda: threading.Thread(target=menu_wrapper(lambda: run_downloader(config, print_output, progress, root)), daemon=True).start()),
    (" 2. Clean & Tag MP3 Files ", lambda: threading.Thread(target=menu_wrapper(lambda: run_cleaner(config, print_output)), daemon=True).start()),
    (" 3. Set Music Folder ", menu_wrapper(lambda: update_and_show(root, text_output, config, "music_folder", "music folder", ask_dir=True))),
    (" 4. Set CSV File Path ", menu_wrapper(lambda: update_and_show(root, text_output, config, "csv_path", "CSV file", ask_filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]))),
    (" 5. Edit Song Tags List ", menu_wrapper(lambda: update_and_show(root, text_output, config, "song_tags", "song tags", is_list=True))),
    (" 6. Edit Web Tags List ", menu_wrapper(lambda: update_and_show(root, text_output, config, "web_tags", "web tags", is_list=True))),
    (" 7. Exit ", root.destroy)
]

for text, command in menu_items:
    btn = tk.Button(
        root,
        text=text,
        command=command,
        bg="#333",
        fg="#F8F8F8",
        activebackground="#444",
        activeforeground="#FFF",
        highlightbackground="#555",
        bd=0,
        font=("Segoe UI", 12),
        width=32,
        height=1
    )
    btn.pack(pady=2)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

# --- Watermark in bottom right ---
watermark_frame = tk.Frame(root, bg="#242424")
watermark_frame.pack(side="bottom", fill="x", anchor="se")
watermark = tk.Label(
    watermark_frame,
    text="v8.0   © 2025",
    bg="#242424",
    fg="#888888",
    font=("Segoe UI", 10, "italic"),
    anchor="e",
    justify="right"
)
watermark.pack(side="right", padx=12, pady=4)

def center_window(win):
    win.update_idletasks()
    w = win.winfo_width()
    h = win.winfo_height()
    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()
    x = (screen_w // 2) - (w // 2)
    y = (screen_h // 2) - (h // 2)
    win.geometry(f'{w}x{h}+{x}+{y}')

center_window(root)

root.update()
print_config_with_line()
root.mainloop()
