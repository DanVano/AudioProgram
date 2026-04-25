import logging, pathlib, sys, traceback
import customtkinter as ctk

from input_handler import update_and_show
from tag_cleaner import run_cleaner, move_to_library
from utils import read_user_config
from ui import (
    build_output_area, build_progressbar, make_print_output,
    build_config_sidebar, center_window, run_in_thread,
)

def excepthook(exc_type, exc, tb):
    try:
        log = pathlib.Path.home() / "AudioProgram_error.log"
        with log.open("a", encoding="utf-8") as f:
            traceback.print_exception(exc_type, exc, tb, file=f)
    except Exception:
        traceback.print_exception(exc_type, exc, tb)
sys.excepthook = excepthook

try:
    from downloader import run_downloader
    DOWNLOADER_AVAILABLE = True
    DOWNLOADER_MSG = "Ready  (yt-dlp)"
except Exception as e:
    DOWNLOADER_AVAILABLE = False
    DOWNLOADER_MSG = f"Disabled — {e}"

logging.getLogger("mutagen").setLevel(logging.ERROR)

config = read_user_config()

# ── Window ────────────────────────────────────────────────────────────────────
root = ctk.CTk()
root.title("Audio Program  v8.0")
root.geometry("1080x1080")
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

# ── Progress bar + status label ───────────────────────────────────────────────
progress = build_progressbar(root)

# ── Config display (textbox header) ──────────────────────────────────────────
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
    song_tags = config.get("song_tags") or []
    web_tags  = config.get("web_tags")  or []
    row("Song Tags",    ", ".join(song_tags if isinstance(song_tags, list) else []))
    row("Website Tags", ", ".join(web_tags  if isinstance(web_tags,  list) else []))
    row("Last Scanned",   config.get("last_scanned_date", "[Not Set]"))
    row("Downloader",     DOWNLOADER_MSG)

    text_output.insert("end", ". . " * 70 + "\n", "dotted")
    text_output.insert("end", "Operational Log:\n", "logtitle")
    text_output.configure(state="disabled")

    # Keep sidebar in sync
    if "_refresh_sidebar" in globals():
        _refresh_sidebar()

# ── Actions ───────────────────────────────────────────────────────────────────
_action_buttons: list = []

def _set_buttons_enabled(enabled: bool):
    state = "normal" if enabled else "disabled"
    for btn in _action_buttons:
        btn.configure(state=state)

def run_task(fn, *args, **kwargs):
    """Disable action buttons, run fn in a daemon thread, re-enable when done."""
    _set_buttons_enabled(False)
    progress.set_status("Running…")
    def _wrapper():
        try:
            fn(*args, **kwargs)
        finally:
            root.after(0, lambda: _set_buttons_enabled(True))
            progress.set_status("Done")
            root.after(2000, lambda: progress.set_status("Idle"))
    run_in_thread(_wrapper)

def start_downloader():
    if not DOWNLOADER_AVAILABLE:
        print_output("Downloader unavailable — check Downloader status in config above.")
        return
    run_task(run_downloader, config, print_output, progress)

def start_cleaner():
    run_task(run_cleaner, config, print_output)

def start_move_to_library():
    run_task(move_to_library, config, print_output)

# ── Button helpers ────────────────────────────────────────────────────────────
BTN_W = 440
BTN_H = 38

def section_label(parent, text):
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(fill="x", pady=(10, 2))

    if text:
        # Left line
        ctk.CTkFrame(frame, height=1, fg_color="#272727").pack(
            side="left", fill="y", expand=True, pady=8, padx=(0, 8))
        ctk.CTkLabel(
            frame,
            text=text,
            font=ctk.CTkFont("Segoe UI", 11),
            text_color="#3a3a3a",
        ).pack(side="left")
        # Right line
        ctk.CTkFrame(frame, height=1, fg_color="#272727").pack(
            side="left", fill="y", expand=True, pady=8, padx=(8, 0))

def make_btn(parent, label, cmd, fg, hover, border_color=None):
    b = ctk.CTkButton(
        parent,
        text=label,
        command=cmd,
        fg_color=fg,
        hover_color=hover,
        text_color="#e0e0e0",
        font=ctk.CTkFont("Segoe UI", 15),
        width=BTN_W,
        height=BTN_H,
        corner_radius=6,
        anchor="w",
        border_width=1,
        border_color=border_color if border_color else fg,
    )
    b.pack(pady=2)
    return b

# ── Bottom layout: buttons (left) + config sidebar (right) ───────────────────
bottom_frame = ctk.CTkFrame(root, fg_color="transparent")
bottom_frame.pack(fill="x", padx=16, pady=(4, 8))

# Buttons column
btn_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
btn_frame.pack(side="left", anchor="n")

section_label(btn_frame, "ACTIONS")
_action_buttons += [
    make_btn(btn_frame, "  ⬇  Run Shazam Downloader",        start_downloader,
             "#1b3a58", "#255080", border_color="#2a5a8a"),
    make_btn(btn_frame, "  ✦  Clean & Tag MP3 Files",         start_cleaner,
             "#1b3a58", "#255080", border_color="#2a5a8a"),
    make_btn(btn_frame, "  →  Move Staged Files to Library",  start_move_to_library,
             "#1b3d28", "#245535", border_color="#2a6040"),
]

section_label(btn_frame, "SETTINGS")
_action_buttons += [
    make_btn(btn_frame, "  📁  Set Library Folder",  lambda: update_and_show(
        root, config, "library_folder", "library folder",
        ask_dir=True, refresh_fn=print_config_with_line),
        "#1c1c1c", "#2a2a2a", border_color="#333333"),
    make_btn(btn_frame, "  📂  Set Staging Folder",  lambda: update_and_show(
        root, config, "staging_folder", "staging folder",
        ask_dir=True, refresh_fn=print_config_with_line),
        "#1c1c1c", "#2a2a2a", border_color="#333333"),
    make_btn(btn_frame, "  📄  Set CSV File Path",   lambda: update_and_show(
        root, config, "csv_path", "CSV file",
        ask_filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
        refresh_fn=print_config_with_line),
        "#1c1c1c", "#2a2a2a", border_color="#333333"),
    make_btn(btn_frame, "  🏷  Edit Song Tags List", lambda: update_and_show(
        root, config, "song_tags", "song tags",
        is_list=True, refresh_fn=print_config_with_line),
        "#1c1c1c", "#2a2a2a", border_color="#333333"),
    make_btn(btn_frame, "  🌐  Edit Web Tags List",  lambda: update_and_show(
        root, config, "web_tags", "web tags",
        is_list=True, refresh_fn=print_config_with_line),
        "#1c1c1c", "#2a2a2a", border_color="#333333"),
]

section_label(btn_frame, "")
make_btn(btn_frame, "  ✕  Exit", root.destroy, "#3d1b1b", "#5c2222", border_color="#5a2525")

# Config sidebar column
_config_sidebar, _refresh_sidebar = build_config_sidebar(
    bottom_frame, config, DOWNLOADER_MSG)
_config_sidebar.pack(side="left", fill="both", expand=True, padx=(14, 0), anchor="n")

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
