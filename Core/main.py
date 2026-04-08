import ctypes
import logging, pathlib, sys, traceback
import tkinter as tk

def _apply_dark_titlebar(root: tk.Tk) -> None:
    """Tell Windows DWM to render the title bar in dark mode."""
    try:
        HWND = ctypes.windll.user32.GetParent(root.winfo_id())
        # Attribute 20 = DWMWA_USE_IMMERSIVE_DARK_MODE (Windows 11 / late Win10)
        # Attribute 19 = same flag on older Windows 10 builds
        for attr in (20, 19):
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                HWND, attr,
                ctypes.byref(ctypes.c_int(1)),
                ctypes.sizeof(ctypes.c_int(1)),
            )
    except Exception:
        pass  # not on Windows or DWM unavailable — fail silently

from input_handler import update_and_show
from tag_cleaner import run_cleaner, move_to_library
from utils import read_user_config
from ui import (
    build_output_area, build_progressbar, make_print_output,
    add_hover, center_window, run_in_thread,
)

def excepthook(exc_type, exc, tb):
    log = pathlib.Path.home() / "AudioProgram_error.log"
    with log.open("a", encoding="utf-8") as f:
        traceback.print_exception(exc_type, exc, tb, file=f)
sys.excepthook = excepthook

try:
    from downloader import run_downloader
    DOWNLOADER_AVAILABLE = True
    DOWNLOADER_MSG = "Ready  (yt-dlp)"
except RuntimeError as e:
    DOWNLOADER_AVAILABLE = False
    DOWNLOADER_MSG = f"Disabled — {e}"

logging.getLogger("mutagen").setLevel(logging.ERROR)

config = read_user_config()

# ── Window ────────────────────────────────────────────────────────────────────
root = tk.Tk()
root.title("Audio Program  v8.0")
root.configure(bg="#1e1e1e")
root.resizable(False, False)

tk.Label(
    root,
    text="MP3 Downloader & Library Manager",
    font=("Segoe UI", 18, "bold"),
    bg="#1e1e1e", fg="#e8e8e8",
).pack(pady=(14, 2))

tk.Label(
    root,
    text="Shazam  →  Download  →  Clean & Tag  →  Library",
    font=("Segoe UI", 9),
    bg="#1e1e1e", fg="#666666",
).pack(pady=(0, 10))

# ── Output area ───────────────────────────────────────────────────────────────
text_output = build_output_area(root)
print_output = make_print_output(root, text_output)

progress = build_progressbar(root)
progress.pack(pady=6)

# ── Config display ────────────────────────────────────────────────────────────
def print_config_with_line():
    text_output.configure(state="normal")
    text_output.delete("1.0", tk.END)

    def row(label, value):
        text_output.insert(tk.END, "   - ")
        text_output.insert(tk.END, label, "bold")
        text_output.insert(tk.END, f":   {value}\n")

    text_output.insert(tk.END, "Current Config:\n", "bold")
    row("Library Folder",  config.get("library_folder",  "[Not Set]"))
    row("Staging Folder",  config.get("staging_folder",  "[Not Set]"))
    row("CSV",             config.get("csv_path",        "[Not Set]"))
    row("Song Tags",       ", ".join(config.get("song_tags", []) or []))
    row("Website Tags",    ", ".join(config.get("web_tags",  []) or []))
    row("Last Scanned",    config.get("last_scanned_date", "[Not Set]"))
    row("Downloader",      DOWNLOADER_MSG)

    text_output.insert(tk.END, ". . " * 70 + "\n", "dotted")
    text_output.insert(tk.END, "Operational Log:\n", "logtitle")
    text_output.configure(state="disabled")

# ── Actions ───────────────────────────────────────────────────────────────────
def start_downloader():
    if not DOWNLOADER_AVAILABLE:
        print_output("Downloader unavailable — check Downloader status in config above.")
        return
    run_in_thread(run_downloader, config, print_output, progress, root)

def start_cleaner():
    run_in_thread(run_cleaner, config, print_output)

def start_move_to_library():
    run_in_thread(move_to_library, config, print_output)

# ── Button helpers ─────────────────────────────────────────────────────────────
BTN_W = 34

def section_label(parent, text):
    tk.Label(
        parent,
        text=text,
        font=("Segoe UI", 8),
        bg="#1e1e1e", fg="#555555",
    ).pack(pady=(10, 2))

def make_btn(parent, label, cmd, bg, hover):
    b = tk.Button(
        parent,
        text=label,
        command=cmd,
        bg=bg, fg="#e8e8e8",
        activebackground=hover, activeforeground="#ffffff",
        highlightbackground="#2a2a2a",
        bd=0,
        font=("Segoe UI", 11),
        width=BTN_W, height=1,
        cursor="hand2",
        anchor="w", padx=14,
    )
    b.pack(pady=2)
    add_hover(b, normal=bg, hover=hover)
    return b

# ── Menu ──────────────────────────────────────────────────────────────────────
btn_frame = tk.Frame(root, bg="#1e1e1e")
btn_frame.pack(pady=(4, 8))

section_label(btn_frame, "──  ACTIONS  ──")
make_btn(btn_frame, "  Run Shazam Downloader",      start_downloader,     "#1b3a58", "#255080")
make_btn(btn_frame, "  Clean & Tag MP3 Files",      start_cleaner,        "#1b3a58", "#255080")
make_btn(btn_frame, "  Move Staged Files to Library", start_move_to_library, "#1b3d28", "#245535")

section_label(btn_frame, "──  SETTINGS  ──")
make_btn(btn_frame, "  Set Library Folder",  lambda: update_and_show(
    root, text_output, config, "library_folder", "library folder", ask_dir=True),
    "#252525", "#343434")
make_btn(btn_frame, "  Set Staging Folder",  lambda: update_and_show(
    root, text_output, config, "staging_folder", "staging folder", ask_dir=True),
    "#252525", "#343434")
make_btn(btn_frame, "  Set CSV File Path",   lambda: update_and_show(
    root, text_output, config, "csv_path", "CSV file",
    ask_filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]),
    "#252525", "#343434")
make_btn(btn_frame, "  Edit Song Tags List", lambda: update_and_show(
    root, text_output, config, "song_tags", "song tags", is_list=True),
    "#252525", "#343434")
make_btn(btn_frame, "  Edit Web Tags List",  lambda: update_and_show(
    root, text_output, config, "web_tags", "web tags", is_list=True),
    "#252525", "#343434")

section_label(btn_frame, "")
make_btn(btn_frame, "  Exit", root.destroy, "#3d1b1b", "#5c2222")

# ── Watermark ─────────────────────────────────────────────────────────────────
wm_frame = tk.Frame(root, bg="#1e1e1e")
wm_frame.pack(side="bottom", fill="x")
tk.Label(
    wm_frame,
    text="v8.0   © 2025",
    bg="#1e1e1e", fg="#3a3a3a",
    font=("Segoe UI", 9, "italic"),
    anchor="e", justify="right",
).pack(side="right", padx=12, pady=4)

center_window(root)
root.update()
_apply_dark_titlebar(root)
print_config_with_line()
root.mainloop()
