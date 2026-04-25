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

    Also supports pulse() / stop_pulse() for indeterminate animation during
    long waits (e.g. active downloads).

    New: set_status(text) updates an optional label below the bar.
    """
    def __init__(self, bar: ctk.CTkProgressBar, root: ctk.CTk,
                 label: ctk.CTkLabel | None = None):
        self._bar   = bar
        self._root  = root
        self._label = label
        self._value   = 0
        self._maximum = 100
        self._pulse_stop: threading.Event | None = None

    def __setitem__(self, key, val):
        if key == "value":
            self._value = int(val)
            if self._pulse_stop is None:
                frac = self._value / self._maximum if self._maximum else 0
                self._root.after(0, lambda f=frac: self._bar.set(min(max(f, 0.0), 1.0)))
        elif key == "maximum":
            self._maximum = max(int(val), 1)

    def __getitem__(self, key):
        return self._value if key == "value" else self._maximum

    def set_status(self, text: str):
        """Update the status label text (thread-safe)."""
        if self._label:
            self._root.after(0, lambda t=text: self._label.configure(text=t))

    def pulse(self):
        """Start a bouncing animation — call before a long blocking operation."""
        if self._pulse_stop is not None:
            return
        stop_evt = threading.Event()
        self._pulse_stop = stop_evt
        self.set_status("Running…")

        def _animate():
            pos, direction = 0.0, 1
            while not stop_evt.is_set():
                self._root.after(0, lambda p=pos: self._bar.set(p))
                stop_evt.wait(0.025)
                pos += 0.025 * direction
                if pos >= 1.0:
                    pos, direction = 1.0, -1
                elif pos <= 0.0:
                    pos, direction = 0.0, 1

        threading.Thread(target=_animate, daemon=True).start()

    def stop_pulse(self):
        """Stop the animation and restore the bar to its determinate position."""
        if self._pulse_stop is None:
            return
        self._pulse_stop.set()
        self._pulse_stop = None
        frac = self._value / self._maximum if self._maximum else 0
        self._root.after(0, lambda: self._bar.set(min(max(frac, 0.0), 1.0)))
        self.set_status("Idle")

    # Geometry delegates (so callers can do progress.pack(...))
    def pack(self, **kw):  self._bar.pack(**kw)
    def grid(self, **kw):  self._bar.grid(**kw)
    def place(self, **kw): self._bar.place(**kw)


# ── Output area ───────────────────────────────────────────────────────────────

def build_output_area(root: ctk.CTk) -> ctk.CTkTextbox:
    textbox = ctk.CTkTextbox(
        root,
        height=380,
        width=950,
        font=("Consolas", 14),
        fg_color="#171717",
        text_color="#d0d0d0",
        scrollbar_button_color="#2e2e2e",
        scrollbar_button_hover_color="#444444",
        border_color="#2a2a2a",
        border_width=1,
        wrap="word",
        state="disabled",
    )
    textbox.pack(fill="both", expand=True, padx=16, pady=(4, 4))

    inner = textbox._textbox
    inner.tag_configure("bold",     font=("Consolas", 14, "bold"))
    inner.tag_configure("logtitle", font=("Consolas", 14, "bold"), foreground="#8ab4f8")
    textbox.tag_config("dotted",    foreground="#383838")
    textbox.tag_config("ok",        foreground="#81c995")
    textbox.tag_config("warn",      foreground="#f9c74f")
    textbox.tag_config("err",       foreground="#f28b82")

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


# ── Progress bar ──────────────────────────────────────────────────────────────

def build_progressbar(parent: ctk.CTk | ctk.CTkFrame) -> ProgressWrapper:
    """
    Creates a progress bar + status label inside a transparent frame.
    Both are packed into `parent`. Returns a ProgressWrapper.
    """
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(pady=(2, 6))

    bar = ctk.CTkProgressBar(
        frame,
        width=600,
        height=5,
        fg_color="#252525",
        progress_color="#4a90d9",
        corner_radius=3,
    )
    bar.set(0)
    bar.pack()

    status_label = ctk.CTkLabel(
        frame,
        text="Idle",
        font=ctk.CTkFont("Segoe UI", 11),
        text_color="#404040",
    )
    status_label.pack(pady=(2, 0))

    return ProgressWrapper(bar, parent, label=status_label)


# ── Config sidebar ────────────────────────────────────────────────────────────

def _truncate(value: str, maxlen: int = 32) -> str:
    if not value or value == "[Not Set]":
        return "[Not Set]"
    return ("…" + value[-(maxlen - 1):]) if len(value) > maxlen else value


def build_config_sidebar(parent, config: dict, downloader_msg: str):
    """
    Build a styled config sidebar frame. Pack it yourself.
    Returns (frame, refresh_fn) — call refresh_fn() after any config change.
    """
    frame = ctk.CTkFrame(
        parent,
        fg_color="#171717",
        border_color="#2a2a2a",
        border_width=1,
        corner_radius=6,
    )

    ctk.CTkLabel(
        frame,
        text="CONFIG",
        font=ctk.CTkFont("Consolas", 10),
        text_color="#404040",
    ).pack(anchor="w", padx=12, pady=(8, 2))

    ctk.CTkFrame(frame, height=1, fg_color="#242424").pack(fill="x", padx=12)

    rows_frame = ctk.CTkFrame(frame, fg_color="transparent")
    rows_frame.pack(fill="both", expand=True, padx=12, pady=(6, 10))

    def _row(key: str, val: str, val_color: str = "#707070"):
        r = ctk.CTkFrame(rows_frame, fg_color="transparent")
        r.pack(fill="x", pady=1)
        ctk.CTkLabel(
            r,
            text=f"  {key}",
            font=ctk.CTkFont("Consolas", 11),
            text_color="#454545",
            width=108,
            anchor="w",
        ).pack(side="left")
        ctk.CTkLabel(
            r,
            text=val,
            font=ctk.CTkFont("Consolas", 11),
            text_color=val_color,
            anchor="w",
        ).pack(side="left", fill="x", expand=True)

    def _divider():
        ctk.CTkFrame(rows_frame, height=1, fg_color="#232323").pack(fill="x", pady=5)

    def refresh():
        for w in rows_frame.winfo_children():
            w.destroy()

        lib  = _truncate(config.get("library_folder", "[Not Set]"))
        stg  = _truncate(config.get("staging_folder", "[Not Set]"))
        csv  = _truncate(config.get("csv_path",        "[Not Set]"))

        _row("Library", lib)
        _row("Staging", stg)
        _row("CSV",     csv)

        _divider()

        song_tags = config.get("song_tags") or []
        web_tags  = config.get("web_tags")  or []

        song_disp = (", ".join(song_tags[:2]) + ("…" if len(song_tags) > 2 else "")) if song_tags else "[Not Set]"
        web_disp  = (", ".join(web_tags[:2])  + ("…" if len(web_tags)  > 2 else "")) if web_tags  else "[Not Set]"

        _row("Song Tags", song_disp)
        _row("Web Tags",  web_disp)

        _divider()

        _row("Last Scan", config.get("last_scanned_date", "[Not Set]"))

        dl_color = "#81c995" if "Ready" in downloader_msg else "#f28b82"
        _row("Downloader", _truncate(downloader_msg, 26), val_color=dl_color)

    refresh()
    return frame, refresh


# ── Utilities ─────────────────────────────────────────────────────────────────

def center_window(win: ctk.CTk):
    win.update_idletasks()
    w, h = win.winfo_width(), win.winfo_height()
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    win.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")


def run_in_thread(fn, *args, **kwargs):
    threading.Thread(target=lambda: fn(*args, **kwargs), daemon=True).start()
