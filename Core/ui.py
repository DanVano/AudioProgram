import re
import tkinter as tk

import threading
from tkinter import ttk

# Detect your final summary lines so labels can be bolded with colons.
_SUMMARY_RE = re.compile(r'^\[INFO\]\s*.+\d(?:\s\|\s.+\d)+$')

def build_output_area(root: tk.Tk) -> tk.Text:
    """Create the output Text area with the same look/feel as before."""
    out_frame = tk.Frame(root, bg="#242424")
    out_frame.pack(fill="both", expand=True, padx=16, pady=6)

    text_output = tk.Text(
        out_frame,
        height=20,
        width=110,
        bg="#242424",
        fg="#F8F8F8",
        insertbackground="#F8F8F8",
        highlightbackground="#333",
        highlightcolor="#444",
        padx=16,
        pady=10,
        font=("Segoe UI", 12),
        wrap="word",
    )
    text_output.pack(side="left", fill="both", expand=True)

    y_scroll = tk.Scrollbar(out_frame, orient="vertical", relief="sunken", command=text_output.yview)
    y_scroll.pack(side="right", fill="y")
    text_output.configure(yscrollcommand=y_scroll.set)

    # Tags identical to your previous setup
    text_output.tag_configure("bold", font=("Segoe UI", 12, "bold"))
    text_output.tag_configure("dotted", foreground="#AAAAAA", spacing1=7, spacing3=2)
    text_output.tag_configure("logtitle", font=("Segoe UI", 12, "bold"), spacing1=2)
    return text_output

def make_print_output(root: tk.Tk, text_output: tk.Text):
    """Return a thread-safe print_output(msg) that preserves your styling."""
    def print_output(msg: str):
        def _append():
            text_output.configure(state="normal")

            # Preserve any leading newlines sent by workers
            leading_newlines = len(msg) - len(msg.lstrip('\n'))
            if leading_newlines:
                text_output.insert(tk.END, "\n" * leading_newlines)

            stripped = msg.lstrip()
            if _SUMMARY_RE.match(stripped):
                # Bold the [INFO] prefix
                text_output.insert(tk.END, "[INFO] ", "bold")

                # Bold each label + colon, normal value
                body = stripped.split("] ", 1)[1] if "] " in stripped else stripped[7:]
                parts = [p.strip() for p in body.split("|")]
                for i, part in enumerate(parts):
                    label, value = (part.rsplit(" ", 1) if " " in part else (part, ""))
                    text_output.insert(tk.END, f"{label}: ", "bold")
                    text_output.insert(tk.END, value)
                    if i < len(parts) - 1:
                        text_output.insert(tk.END, " | ")
                text_output.insert(tk.END, "\n")
            else:
                text_output.insert(tk.END, msg + "\n")

            text_output.see(tk.END)
            text_output.configure(state="disabled")
        root.after(0, _append)
    return print_output

def build_progressbar(root: tk.Tk) -> ttk.Progressbar:
    """Create the same custom-styled progressbar used before."""
    style = ttk.Style()
    style.theme_use("default")
    style.configure(
        "Custom.Horizontal.TProgressbar",
        troughcolor="#444444",
        background="#d6d6d6",
        bordercolor="#555555",
        thickness=18,
    )
    return ttk.Progressbar(
        root,
        orient="horizontal",
        length=400,
        mode="determinate",
        style="Custom.Horizontal.TProgressbar",
    )

def add_hover(widget: tk.Widget, normal="#333", hover="#555555"):
    """Apply the same hover effect you had on buttons."""
    def on_enter(_): widget["bg"] = hover
    def on_leave(_): widget["bg"] = normal
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

def center_window(win: tk.Tk):
    """Center the window on screen."""
    win.update_idletasks()
    w = win.winfo_width()
    h = win.winfo_height()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = (sw // 2) - (w // 2)
    y = (sh // 2) - (h // 2)
    win.geometry(f"{w}x{h}+{x}+{y}")

def run_in_thread(fn, *args, **kwargs):
    """Start a daemon thread for long-running tasks (keeps UI responsive)."""
    threading.Thread(target=lambda: fn(*args, **kwargs), daemon=True).start()
