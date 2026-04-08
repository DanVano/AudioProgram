import logging, pathlib, sys, traceback
import customtkinter as ctk

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
# CTk handles dark title bar automatically on Windows 10/11
root = ctk.CTk()
root.title("Audio Program  v8.0")
root.geometry("1080x1170")
root.resizable(False, False)

ctk.CTkLabel(
    root,
    text="MP3 Downloader & Library Manager",
    font=ctk.CTkFont("Segoe UI", 26, weight="bold"),
    text_color="#e8e8e8",
).pack(pady=(14, 2))

ctk.CTkLabel(
    root,
    text="Shazam  →  Download  →  Clean & Tag  →  Library",
    font=ctk.CTkFont("Segoe UI", 14),
    text_color="#999999",
).pack(pady=(0, 10))

# ── Output area ───────────────────────────────────────────────────────────────
text_output = build_output_area(root)
print_output = make_print_output(root, text_output)

progress = build_progressbar(root)
progress.pack(pady=6)

# ── Config display ────────────────────────────────────────────────────────────
def print_config_with_line():
    text_output.configure(state="normal")
    text_output.delete("1.0", "end")

    def row(label, value):
        text_output.insert("end", "   - ")
        text_output.insert("end", label, "bold")
        text_output.insert("end", f":   {value}\n")

    text_output.insert("end", "Current Config:\n", "bold")
    row("Library Folder", config.get("library_folder", "[Not Set]"))
    row("Staging Folder", config.get("staging_folder", "[Not Set]"))
    row("CSV",            config.get("csv_path",        "[Not Set]"))
    row("Song Tags",      ", ".join(config.get("song_tags", []) or []))
    row("Website Tags",   ", ".join(config.get("web_tags",  []) or []))
    row("Last Scanned",   config.get("last_scanned_date", "[Not Set]"))
    row("Downloader",     DOWNLOADER_MSG)

    text_output.insert("end", ". . " * 70 + "\n", "dotted")
    text_output.insert("end", "Operational Log:\n", "logtitle")
    text_output.configure(state="disabled")

# ── Actions ───────────────────────────────────────────────────────────────────
_action_buttons: list = []

def _set_buttons_enabled(enabled: bool):
    state = "normal" if enabled else "disabled"
    for btn in _action_buttons:
        btn.configure(state=state)

def run_task(fn, *args, **kwargs):
    """Disable action buttons, run fn in a daemon thread, re-enable when done."""
    _set_buttons_enabled(False)
    def _wrapper():
        try:
            fn(*args, **kwargs)
        finally:
            root.after(0, lambda: _set_buttons_enabled(True))
    run_in_thread(_wrapper)

def start_downloader():
    if not DOWNLOADER_AVAILABLE:
        print_output("Downloader unavailable — check Downloader status in config above.")
        return
    run_task(run_downloader, config, print_output, progress, root)

def start_cleaner():
    run_task(run_cleaner, config, print_output)

def start_move_to_library():
    run_task(move_to_library, config, print_output)

# ── Button helpers ────────────────────────────────────────────────────────────
BTN_W = 440
BTN_H = 38

def section_label(parent, text):
    ctk.CTkLabel(
        parent,
        text=text,
        font=ctk.CTkFont("Segoe UI", 13),
        text_color="#505050",
    ).pack(pady=(10, 2))

def make_btn(parent, label, cmd, fg, hover):
    b = ctk.CTkButton(
        parent,
        text=label,
        command=cmd,
        fg_color=fg,
        hover_color=hover,
        text_color="#e8e8e8",
        font=ctk.CTkFont("Segoe UI", 15),
        width=BTN_W,
        height=BTN_H,
        corner_radius=6,
        anchor="w",
    )
    b.pack(pady=2)
    return b

# ── Menu ──────────────────────────────────────────────────────────────────────
btn_frame = ctk.CTkFrame(root, fg_color="transparent")
btn_frame.pack(pady=(4, 8))

section_label(btn_frame, "──  ACTIONS  ──")
_action_buttons += [
    make_btn(btn_frame, "  Run Shazam Downloader",        start_downloader,      "#1b3a58", "#255080"),
    make_btn(btn_frame, "  Clean & Tag MP3 Files",        start_cleaner,         "#1b3a58", "#255080"),
    make_btn(btn_frame, "  Move Staged Files to Library", start_move_to_library, "#1b3d28", "#245535"),
]

section_label(btn_frame, "──  SETTINGS  ──")
make_btn(btn_frame, "  Set Library Folder",  lambda: update_and_show(
    root, text_output, config, "library_folder", "library folder",
    ask_dir=True, refresh_fn=print_config_with_line),
    "#1c1c1c", "#2a2a2a")
make_btn(btn_frame, "  Set Staging Folder",  lambda: update_and_show(
    root, text_output, config, "staging_folder", "staging folder",
    ask_dir=True, refresh_fn=print_config_with_line),
    "#1c1c1c", "#2a2a2a")
make_btn(btn_frame, "  Set CSV File Path",   lambda: update_and_show(
    root, text_output, config, "csv_path", "CSV file",
    ask_filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
    refresh_fn=print_config_with_line),
    "#1c1c1c", "#2a2a2a")
make_btn(btn_frame, "  Edit Song Tags List", lambda: update_and_show(
    root, text_output, config, "song_tags", "song tags",
    is_list=True, refresh_fn=print_config_with_line),
    "#1c1c1c", "#2a2a2a")
make_btn(btn_frame, "  Edit Web Tags List",  lambda: update_and_show(
    root, text_output, config, "web_tags", "web tags",
    is_list=True, refresh_fn=print_config_with_line),
    "#1c1c1c", "#2a2a2a")

section_label(btn_frame, "")
make_btn(btn_frame, "  Exit", root.destroy, "#3d1b1b", "#5c2222")

# ── Watermark ─────────────────────────────────────────────────────────────────
wm_frame = ctk.CTkFrame(root, fg_color="transparent")
wm_frame.pack(side="bottom", fill="x")
ctk.CTkLabel(
    wm_frame,
    text="v8.0   © 2025",
    font=ctk.CTkFont("Segoe UI", 13, slant="italic"),
    text_color="#3a3a3a",
).pack(side="right", padx=12, pady=4)

center_window(root)
print_config_with_line()
root.mainloop()
