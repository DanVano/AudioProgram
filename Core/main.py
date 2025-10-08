import logging
import tkinter as tk

from input_handler import update_and_show
from tag_cleaner import run_cleaner
from utils import read_user_config

from ui import (
    build_output_area,
    build_progressbar,
    make_print_output,
    add_hover,
    center_window,
    run_in_thread,
)

# Safe importer: keep UI running without a key
try:
    from downloader import run_downloader  # may raise RuntimeError if no key
    DOWNLOADER_AVAILABLE = True
    DOWNLOADER_MSG = "Downloader: Ready"
except RuntimeError as e:
    DOWNLOADER_AVAILABLE = False
    DOWNLOADER_MSG = f"Downloader: Disabled — {e}"

# Silence mutagen’s noisy warnings in the console
logging.getLogger("mutagen").setLevel(logging.ERROR)

# Load config once and pass it around
config = read_user_config()

# === GUI Setup ===
root = tk.Tk()
root.title("Audio Program v8.0")
root.configure(bg="#242424")

header = tk.Label(
    root,
    text="MP3 Downloader and Filename Cleaner",
    font=("Segoe UI", 20, "bold"),
    bg="#242424",
    fg="#F8F8F8",
)
header.pack(pady=(12, 6))

# Output area + printer
text_output = build_output_area(root)
print_output = make_print_output(root, text_output)

# Progress bar (identical style as before)
progress = build_progressbar(root)
progress.pack(pady=6)

def print_config_with_line():
    text_output.configure(state="normal")
    text_output.delete("1.0", tk.END)

    text_output.insert(tk.END, "Current Config:\n", "bold")

    text_output.insert(tk.END, "   - "); text_output.insert(tk.END, "Music Folder", "bold")
    text_output.insert(tk.END, f":   {config.get('music_folder', '[Not Set]')}\n")

    text_output.insert(tk.END, "   - "); text_output.insert(tk.END, "CSV", "bold")
    text_output.insert(tk.END, f":   {config.get('csv_path', '[Not Set]')}\n")

    text_output.insert(tk.END, "   - "); text_output.insert(tk.END, "Song Tags", "bold")
    text_output.insert(tk.END, f":   {', '.join(config.get('song_tags', []) or [])}\n")

    text_output.insert(tk.END, "   - "); text_output.insert(tk.END, "Website Tags", "bold")
    text_output.insert(tk.END, f":   {', '.join(config.get('web_tags', []) or [])}\n")

    text_output.insert(tk.END, "   - "); text_output.insert(tk.END, "Last Scanned", "bold")
    text_output.insert(tk.END, f":   {config.get('last_scanned_date', '[Not Set]')}\n")

    text_output.insert(tk.END, "   - "); text_output.insert(tk.END, "Downloader Status", "bold")
    text_output.insert(tk.END, f":   {DOWNLOADER_MSG}\n", "bold")

    text_output.insert(tk.END, ". . " * 70 + "\n", "dotted")
    text_output.insert(tk.END, "Operational Log:\n", "logtitle")
    text_output.configure(state="disabled")

# === Menu ===
def start_downloader():
    if not DOWNLOADER_AVAILABLE:
        print_output("Downloader disabled (no RAPIDAPI key).")
        return
    run_in_thread(run_downloader, config, print_output, progress, root)

def start_cleaner():
    run_in_thread(run_cleaner, config, print_output)

menu_items = [
    (" 1. Run Shazam Downloader ", start_downloader),
    (" 2. Clean & Tag MP3 Files ", start_cleaner),
    (" 3. Set Music Folder ", lambda: update_and_show(
        root, text_output, config, "music_folder", "music folder", ask_dir=True
    )),
    (" 4. Set CSV File Path ", lambda: update_and_show(
        root, text_output, config, "csv_path", "CSV file",
        ask_filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
    )),
    (" 5. Edit Song Tags List ", lambda: update_and_show(
        root, text_output, config, "song_tags", "song tags", is_list=True
    )),
    (" 6. Edit Web Tags List ", lambda: update_and_show(
        root, text_output, config, "web_tags", "web tags", is_list=True
    )),
    (" 7. Exit ", root.destroy),
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
        height=1,
    )
    btn.pack(pady=2)
    add_hover(btn, normal="#333", hover="#555555")

# Watermark (unchanged)
watermark_frame = tk.Frame(root, bg="#242424")
watermark_frame.pack(side="bottom", fill="x", anchor="se")
watermark = tk.Label(
    watermark_frame,
    text="v8.0   © 2025",
    bg="#242424",
    fg="#888888",
    font=("Segoe UI", 10, "italic"),
    anchor="e",
    justify="right",
)
watermark.pack(side="right", padx=12, pady=4)

center_window(root)
root.update()
print_config_with_line()
root.mainloop()