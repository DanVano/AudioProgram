import re
import threading
import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Matches summary lines like: [INFO] Label1 X | Label2 Y | Label3 Z
_SUMMARY_RE = re.compile(r'^\[INFO\]\s*.+\d(?:\s\|\s.+\d)+$')


class ProgressWrapper:
    """
    Translates ttk-style progress["value"] / progress["maximum"] assignments
    into CTkProgressBar.set() calls so downloader.py needs no changes.
    """
    def __init__(self, bar: ctk.CTkProgressBar):
        self._bar = bar
        self._value   = 0
        self._maximum = 100

    def __setitem__(self, key, val):
        if key == "value":
            self._value = int(val)
            frac = self._value / self._maximum if self._maximum else 0
            self._bar.set(min(max(frac, 0.0), 1.0))
        elif key == "maximum":
            self._maximum = max(int(val), 1)

    def __getitem__(self, key):
        return self._value if key == "value" else self._maximum

    # Delegate geometry methods so callers can do progress.pack(...)
    def pack(self, **kw):  self._bar.pack(**kw)
    def grid(self, **kw):  self._bar.grid(**kw)
    def place(self, **kw): self._bar.place(**kw)


def build_output_area(root: ctk.CTk) -> ctk.CTkTextbox:
    textbox = ctk.CTkTextbox(
        root,
        height=280,
        width=700,
        font=("Consolas", 11),
        fg_color="#1a1a1a",
        text_color="#d0d0d0",
        scrollbar_button_color="#2e2e2e",
        scrollbar_button_hover_color="#444444",
        border_color="#2a2a2a",
        border_width=1,
        wrap="word",
        state="disabled",
    )
    textbox.pack(fill="both", expand=True, padx=16, pady=(4, 4))

    # Tag config forwarded to the underlying tk.Text widget
    textbox.tag_config("bold",     font=("Consolas", 11, "bold"))
    textbox.tag_config("dotted",   foreground="#383838")
    textbox.tag_config("logtitle", font=("Consolas", 11, "bold"), foreground="#8ab4f8")
    textbox.tag_config("ok",       foreground="#81c995")
    textbox.tag_config("warn",     foreground="#f9c74f")
    textbox.tag_config("err",      foreground="#f28b82")

    return textbox


def make_print_output(root: ctk.CTk, textbox: ctk.CTkTextbox):
    """Return a thread-safe print_output(msg) with colour-coded prefixes."""
    def print_output(msg: str):
        def _append():
            textbox.configure(state="normal")

            leading = len(msg) - len(msg.lstrip('\n'))
            if leading:
                textbox.insert("end", "\n" * leading)

            stripped = msg.lstrip()

            if _SUMMARY_RE.match(stripped):
                textbox.insert("end", "[INFO] ", "bold")
                body = stripped.split("] ", 1)[1] if "] " in stripped else stripped[7:]
                parts = [p.strip() for p in body.split("|")]
                for i, part in enumerate(parts):
                    label, value = (part.rsplit(" ", 1) if " " in part else (part, ""))
                    textbox.insert("end", f"{label}: ", "bold")
                    textbox.insert("end", value)
                    if i < len(parts) - 1:
                        textbox.insert("end", " | ")
                textbox.insert("end", "\n")
            elif stripped.startswith(("[OK]", "[MOVED]")):
                textbox.insert("end", msg + "\n", "ok")
            elif stripped.startswith("[SKIP]"):
                textbox.insert("end", msg + "\n", "warn")
            elif stripped.startswith(("[ERROR]", "[WARN]")):
                textbox.insert("end", msg + "\n", "err")
            else:
                textbox.insert("end", msg + "\n")

            textbox.see("end")
            textbox.configure(state="disabled")

        root.after(0, _append)
    return print_output


def build_progressbar(root: ctk.CTk) -> ProgressWrapper:
    bar = ctk.CTkProgressBar(
        root,
        width=420,
        height=6,
        fg_color="#252525",
        progress_color="#4a90d9",
        corner_radius=3,
    )
    bar.set(0)
    return ProgressWrapper(bar)


def add_hover(widget, normal: str, hover: str):
    pass  # CTkButton handles hover natively via hover_color — no-op kept for compat


def center_window(win: ctk.CTk):
    win.update_idletasks()
    w, h = win.winfo_width(), win.winfo_height()
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    win.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")


def run_in_thread(fn, *args, **kwargs):
    threading.Thread(target=lambda: fn(*args, **kwargs), daemon=True).start()
