import logging, pathlib, sys, traceback, datetime
import customtkinter as ctk

from input_handler import update_and_show
from tag_cleaner import run_cleaner, move_to_library
from utils import read_user_config
from ui import (
    build_output_area, build_progressbar, make_print_output,
    build_config_sidebar, build_last_run_bar, update_last_run,
    init_output_log, ToastManager, center_window, run_in_thread,
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
root.title("Audio Program  v9.0")
root.geometry("1080x1040")
root.resizable(False, False)

# ── Header ────────────────────────────────────────────────────────────────────
ctk.CTkLabel(
    root,
    text="MP3 Downloader & Library Manager",
    font=ctk.CTkFont("Segoe UI", 26, weight="bold"),
    text_color="#e8e8e8",
).pack(pady=(11, 2))

ctk.CTkLabel(
    root,
    text="Shazam  →  Download  →  Clean & Tag  →  Library",
    font=ctk.CTkFont("Segoe UI", 14),
    text_color="#b0b0b0",
).pack(pady=(0, 8))

# ── Output area ───────────────────────────────────────────────────────────────
text_output = build_output_area(root)
print_output = make_print_output(root, text_output)
init_output_log(text_output)

# ── Progress bar + status label ───────────────────────────────────────────────
progress = build_progressbar(root)

# ── Last run summary bar ──────────────────────────────────────────────────────
last_run_label = build_last_run_bar(root)

# ── Toast manager ─────────────────────────────────────────────────────────────
toast = ToastManager(root)

# ── Actions ───────────────────────────────────────────────────────────────────
_action_buttons: list = []

def _set_buttons_enabled(enabled: bool):
    state = "normal" if enabled else "disabled"
    for btn in _action_buttons:
        btn.configure(state=state)

def run_task(fn, task_name: str, *args, **kwargs):
    """Disable buttons, run fn in thread, re-enable + show summary when done."""
    _set_buttons_enabled(False)
    progress.set_status("Running…")

    def _wrapper():
        ok = skipped = errors = 0
        try:
            result = fn(*args, **kwargs)
            # fn may return a dict like {"ok": N, "skipped": N, "errors": N}
            if isinstance(result, dict):
                ok      = result.get("ok",      0)
                skipped = result.get("skipped",  0)
                errors  = result.get("errors",   0)
        except Exception as e:
            errors = 1
            print_output(f"[ERROR] {e}")
        finally:
            level = "err" if errors else ("warn" if skipped else "ok")
            msg   = f"✓ {task_name} — {ok} ok"
            if skipped: msg += f"  ·  {skipped} skipped"
            if errors:  msg += f"  ·  {errors} errors"

            root.after(0, lambda: _set_buttons_enabled(True))
            root.after(0, lambda: progress.set_status("Done"))
            root.after(2000, lambda: progress.set_status("Idle"))
            toast.show(msg, level)
            update_last_run(last_run_label, task_name, ok, skipped, errors)

    run_in_thread(_wrapper)

def start_downloader():
    if not DOWNLOADER_AVAILABLE:
        print_output("Downloader unavailable — check Downloader status in config.")
        return
    run_task(run_downloader, "Shazam Downloader", config, print_output, progress)

def start_cleaner():
    run_task(run_cleaner, "Clean & Tag", config, print_output)

def start_move_to_library():
    run_task(move_to_library, "Move to Library", config, print_output)

# ── Config sidebar refresh ────────────────────────────────────────────────────
_config_refresh_fn = None

def refresh_config():
    if _config_refresh_fn:
        _config_refresh_fn()

# ── Button helpers ────────────────────────────────────────────────────────────
BTN_W = 440
BTN_H = 34

def section_label(parent, text: str):
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(fill="x", pady=(9, 2))
    if text:
        ctk.CTkFrame(frame, height=1, fg_color="#272727").pack(
            side="left", expand=True, fill="y", pady=6, padx=(0, 8))
        ctk.CTkLabel(
            frame,
            text=text,
            font=ctk.CTkFont("Segoe UI", 11, weight="bold"),
            text_color="#8ab4f8",
        ).pack(side="left")
        ctk.CTkFrame(frame, height=1, fg_color="#272727").pack(
            side="left", expand=True, fill="y", pady=6, padx=(8, 0))

def make_btn(parent, label, cmd, fg, hover, border_left_color=None):
    b = ctk.CTkButton(
        parent,
        text=label,
        command=cmd,
        fg_color=fg,
        hover_color=hover,
        text_color="#e0e0e0",
        font=ctk.CTkFont("Segoe UI", 14),
        width=BTN_W,
        height=BTN_H,
        corner_radius=6,
        anchor="w",
        border_width=1,
        border_color=border_left_color if border_left_color else fg,
    )
    b.pack(pady=2)
    return b

# ── Bottom layout ─────────────────────────────────────────────────────────────
bottom_frame = ctk.CTkFrame(root, fg_color="transparent")
bottom_frame.pack(fill="x", padx=16, pady=(0, 0))

# Buttons column
btn_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
btn_frame.pack(side="left", anchor="n")

section_label(btn_frame, "ACTIONS")
_action_buttons += [
    make_btn(btn_frame, "  ⬇  Run Shazam Downloader",       start_downloader,
             "#1b3a58", "#255080", "#2a5a8a"),
    make_btn(btn_frame, "  ✦  Clean & Tag MP3 Files",        start_cleaner,
             "#1b3a58", "#255080", "#2a5a8a"),
    make_btn(btn_frame, "  →  Move Staged Files to Library", start_move_to_library,
             "#1b3d28", "#245535", "#2a6040"),
]

section_label(btn_frame, "SETTINGS")
_action_buttons += [
    make_btn(btn_frame, "  📁  Set Library Folder", lambda: update_and_show(
        root, config, "library_folder", "library folder",
        ask_dir=True, refresh_fn=refresh_config),
        "#1c1c1c", "#2a2a2a", "#333333"),
    make_btn(btn_frame, "  📂  Set Staging Folder", lambda: update_and_show(
        root, config, "staging_folder", "staging folder",
        ask_dir=True, refresh_fn=refresh_config),
        "#1c1c1c", "#2a2a2a", "#333333"),
    make_btn(btn_frame, "  📄  Set CSV File Path",  lambda: update_and_show(
        root, config, "csv_path", "CSV file",
        ask_filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
        refresh_fn=refresh_config),
        "#1c1c1c", "#2a2a2a", "#333333"),
    make_btn(btn_frame, "  🏷  Edit Song Tags List", lambda: update_and_show(
        root, config, "song_tags", "song tags",
        is_list=True, refresh_fn=refresh_config),
        "#1c1c1c", "#2a2a2a", "#333333"),
    make_btn(btn_frame, "  🌐  Edit Web Tags List",  lambda: update_and_show(
        root, config, "web_tags", "web tags",
        is_list=True, refresh_fn=refresh_config),
        "#1c1c1c", "#2a2a2a", "#333333"),
]

section_label(btn_frame, "")
make_btn(btn_frame, "  ✕  Exit", root.destroy, "#3d1b1b", "#5c2222", "#5a2525")

# Config sidebar column
_config_sidebar, _config_refresh_fn = build_config_sidebar(
    bottom_frame, config, DOWNLOADER_MSG)
_config_sidebar.pack(side="left", fill="both", expand=True,
                     padx=(14, 0), anchor="n", pady=(29, 0))

# ── Watermark ─────────────────────────────────────────────────────────────────
wm_frame = ctk.CTkFrame(root, fg_color="transparent")
wm_frame.pack(side="bottom", fill="x")
ctk.CTkLabel(
    wm_frame,
    text="v9.0   © 2026",
    font=ctk.CTkFont("Segoe UI", 11, slant="italic"),
    text_color="#888888",
).pack(side="right", padx=12, pady=(0, 4))

center_window(root)
root.mainloop()
