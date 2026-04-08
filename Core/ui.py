import re
import tkinter as tk
import threading
from tkinter import ttk

# Matches summary lines like: [INFO] Label1 X | Label2 Y | Label3 Z
_SUMMARY_RE = re.compile(r'^\[INFO\]\s*.+\d(?:\s\|\s.+\d)+$')

_BG       = "#1e1e1e"
_LOG_BG   = "#1a1a1a"
_FG       = "#d0d0d0"
_TROUGH   = "#2e2e2e"
_PROGRESS = "#4a90d9"

# ── TTK styles (configured once at import time) ───────────────────────────────
_style = ttk.Style()
_style.theme_use("default")

_style.configure(
    "Custom.Horizontal.TProgressbar",
    troughcolor=_TROUGH,
    background=_PROGRESS,
    bordercolor="#2a2a2a",
    thickness=6,
)
_style.configure(
    "Dark.Vertical.TScrollbar",
    background="#2a2a2a",
    troughcolor="#141414",
    arrowcolor="#4a4a4a",
    bordercolor="#1e1e1e",
    darkcolor="#1e1e1e",
    lightcolor="#2a2a2a",
    relief="flat",
)
_style.map(
    "Dark.Vertical.TScrollbar",
    background=[("active", "#3a3a3a"), ("pressed", "#4a4a4a")],
    arrowcolor=[("active", "#888888")],
)

def build_output_area(root: tk.Tk) -> tk.Text:
    out_frame = tk.Frame(root, bg=_BG, padx=0, pady=0)
    out_frame.pack(fill="both", expand=True, padx=16, pady=(4, 4))

    text_output = tk.Text(
        out_frame,
        height=18,
        width=108,
        bg=_LOG_BG, fg=_FG,
        insertbackground=_FG,
        highlightbackground="#2a2a2a",
        highlightcolor="#3a3a3a",
        highlightthickness=1,
        padx=14, pady=10,
        font=("Consolas", 11),
        wrap="word",
        relief="flat",
    )
    text_output.pack(side="left", fill="both", expand=True)

    y_scroll = ttk.Scrollbar(
        out_frame, orient="vertical",
        style="Dark.Vertical.TScrollbar",
        command=text_output.yview,
    )
    y_scroll.pack(side="right", fill="y")
    text_output.configure(yscrollcommand=y_scroll.set)

    text_output.tag_configure("bold",     font=("Consolas", 11, "bold"))
    text_output.tag_configure("dotted",   foreground="#383838", spacing1=6, spacing3=2)
    text_output.tag_configure("logtitle", font=("Consolas", 11, "bold"), foreground="#8ab4f8", spacing1=2)
    text_output.tag_configure("ok",       foreground="#81c995")
    text_output.tag_configure("warn",     foreground="#f9c74f")
    text_output.tag_configure("err",      foreground="#f28b82")

    return text_output

def make_print_output(root: tk.Tk, text_output: tk.Text):
    """Return a thread-safe print_output(msg) with colour-coded prefixes."""
    def print_output(msg: str):
        def _append():
            text_output.configure(state="normal")

            leading = len(msg) - len(msg.lstrip('\n'))
            if leading:
                text_output.insert(tk.END, "\n" * leading)

            stripped = msg.lstrip()

            if _SUMMARY_RE.match(stripped):
                # Bold [INFO] prefix + bold labels, plain values
                text_output.insert(tk.END, "[INFO] ", "bold")
                body = stripped.split("] ", 1)[1] if "] " in stripped else stripped[7:]
                parts = [p.strip() for p in body.split("|")]
                for i, part in enumerate(parts):
                    label, value = (part.rsplit(" ", 1) if " " in part else (part, ""))
                    text_output.insert(tk.END, f"{label}: ", "bold")
                    text_output.insert(tk.END, value)
                    if i < len(parts) - 1:
                        text_output.insert(tk.END, " | ")
                text_output.insert(tk.END, "\n")

            elif stripped.startswith("[OK]"):
                text_output.insert(tk.END, msg + "\n", "ok")
            elif stripped.startswith("[SKIP]"):
                text_output.insert(tk.END, msg + "\n", "warn")
            elif stripped.startswith("[ERROR]") or stripped.startswith("[WARN]"):
                text_output.insert(tk.END, msg + "\n", "err")
            elif stripped.startswith("[MOVED]"):
                text_output.insert(tk.END, msg + "\n", "ok")
            else:
                text_output.insert(tk.END, msg + "\n")

            text_output.see(tk.END)
            text_output.configure(state="disabled")

        root.after(0, _append)
    return print_output

def build_progressbar(root: tk.Tk) -> ttk.Progressbar:
    return ttk.Progressbar(
        root,
        orient="horizontal",
        length=420,
        mode="determinate",
        style="Custom.Horizontal.TProgressbar",
    )

def add_hover(widget: tk.Widget, normal: str, hover: str):
    widget.bind("<Enter>", lambda _: widget.configure(bg=hover))
    widget.bind("<Leave>", lambda _: widget.configure(bg=normal))

def center_window(win: tk.Tk):
    win.update_idletasks()
    w, h = win.winfo_width(), win.winfo_height()
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    win.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

def run_in_thread(fn, *args, **kwargs):
    threading.Thread(target=lambda: fn(*args, **kwargs), daemon=True).start()
