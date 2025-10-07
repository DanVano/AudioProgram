import eyed3, os, re

from datetime import datetime


def _strip_tokens(text, patterns):
    for pat in patterns:
        text = re.sub(pat, "", text, flags=re.IGNORECASE)
    return text

def clean_filename(filename, song_tags, web_tags):
    name, ext = os.path.splitext(filename)
    if not ext:
        ext = ".mp3"

    # 1) Normalize a bit
    name = name.replace("_", " ")

    # 2) Remove user-config tags first (exact text, case-insensitive)
    for tag in (song_tags or []) + (web_tags or []):
        t = tag.strip()
        if t:
            name = re.sub(re.escape(t), "", name, flags=re.IGNORECASE)

    # 3) Strip bracketed junk like [Lyrics], (Official Audio), etc.
    bracket_tokens = r"(official|lyrics?|lyric\s*video|visualizer|audio|video|mv|hq|hd|music\s*video|radio\s*edit|extended\s*mix)"
    name = re.sub(rf"\[\s*{bracket_tokens}\s*\]", "", name, flags=re.IGNORECASE)
    name = re.sub(rf"\(\s*{bracket_tokens}\s*\)", "", name, flags=re.IGNORECASE)

    # 4) Remove common descriptors even when unbracketed
    #    (covers single words AND combos like "Official Lyric Visualizer")
    name = _strip_tokens(name, [
        r"\bofficial(?:\s+music\s+video)?\b",
        r"\blyrics?\b",
        r"\blyric\s*video\b",
        r"\bvisualizer\b",
        r"\baudio(?:\s+only)?\b",
        r"\bmusic\s*video\b",
        r"\bvideo\b",
        r"\bhq\b",
        r"\bhd\b",
        r"\bmv\b",
        r"\b320\s*kbps\b",
        r"\bradio\s*edit\b",
        r"\bextended\s*mix\b",
    ])

    # 5) Tidy separators/spaces/double dashes
    name = re.sub(r"\s*-\s*", " - ", name)     # normalize dashes
    name = re.sub(r"\s{2,}", " ", name).strip()
    name = re.sub(r"^-\s*|\s*-$", "", name)    # strip leading/trailing dash

    return f"{name}{ext}"

def set_id3_tags(filepath, artist, title):
    """
    Returns one of: "ok", "unable", "error"
      ok      -> tags written
      unable  -> mp3 couldn't be loaded by eyeD3
      error   -> exception while saving tags (permission/other)
    """
    audio = eyed3.load(filepath)
    if audio is None:
        print(f"Warning: Could not load file: {filepath}. ID3 tags not set.")
        return "unable"

    if audio.tag is None:
        audio.initTag()

    audio.tag.artist = artist
    audio.tag.album_artist = artist
    audio.tag.title = title
    try:
        audio.tag.save()
        return "ok"
    except PermissionError:
        print(f"Permission denied: {filepath} is read-only.")
    except Exception as e:
        print(f"Error saving ID3 tags to {filepath}: {e}")
    return "error"

def parse_shazam_csv(file_path):
    import csv
    result = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f, fieldnames=["Index", "TagTime", "Title", "Artist", "URL", "TrackKey"])
            next(reader, None)
            for row in reader:
                try:
                    tag_time = datetime.strptime(row["TagTime"], "%Y-%m-%dT%H:%M:%S")
                    result.append({
                        'date': tag_time,
                        'artist': row["Artist"],
                        'title': row["Title"],
                        'combined_track_info': f"{row['Artist']} - {row['Title']}"
                    })
                except ValueError as ve:
                    print(f"Skipping row with invalid date: {row['TagTime']} - {ve}")
    except FileNotFoundError:
        print(f"Error: CSV file not found at path: {file_path}")
    except Exception as e:
        print(f"Error reading CSV: {e}")
    return result

def run_cleaner(config, print_output):
    """
    Cleans MP3 filenames in the configured music_folder and sets basic ID3 tags.
    Final line now shows:
      [INFO] ... | Errors X | Unable to load mp3 Y
    """
    import logging
    music_folder = config.get("music_folder")
    if not music_folder or not os.path.isdir(music_folder):
        print_output(f"[INFO] Music folder not found: {music_folder or '[Not Set]'}")
        return

    files = [f for f in os.listdir(music_folder) if f.lower().endswith(".mp3")]
    files.sort(key=str.lower)

    cleaned = 0
    skipped = 0
    tagged = 0

    # New counters
    errors = 0                 # program/logic errors + mutagen warnings we treat as errors
    unable_to_load = 0         # "Warning: Could not load file: ..." cases

    print_output("[INFO] Running MP3 filename cleaner")

    # --- Capture mutagen warnings like "LAME tag CRC check failed" as Errors ---
    mut_logger = logging.getLogger("mutagen")
    _prev_level = mut_logger.level
    _prev_propagate = getattr(mut_logger, "propagate", True)

    class _MutagenCounter(logging.Handler):
        def __init__(self):
            super().__init__(level=logging.WARNING)
            self.count = 0
        def emit(self, record):
            msg = record.getMessage().lower()
            # Count classic bad-mp3 messages + any mutagen ERRORs
            if "lame tag crc check failed" in msg or record.levelno >= logging.ERROR:
                self.count += 1

    _h = _MutagenCounter()
    mut_logger.addHandler(_h)
    # ensure warnings are emitted while we run (even if main.py changed the level)
    mut_logger.setLevel(logging.WARNING)
    # keep console quiet or noisy — your choice. We leave default propagate as-is.
    try:
        for idx, filename in enumerate(files, start=1):
            try:
                source_path = os.path.join(music_folder, filename)
                print_output(f"{idx}] {filename}")

                # Build cleaned filename using user-config tags
                cleaned_name = clean_filename(
                    filename,
                    config.get("song_tags", []),
                    config.get("web_tags", [])
                )
                target_path = os.path.join(music_folder, cleaned_name)

                # Rename if needed (ensure uniqueness)
                if cleaned_name != filename:
                    base, ext = os.path.splitext(cleaned_name)
                    candidate = cleaned_name
                    n = 2
                    while os.path.exists(target_path):
                        candidate = f"{base} ({n}){ext}"
                        target_path = os.path.join(music_folder, candidate)
                        n += 1
                    os.rename(source_path, target_path)
                    print_output(f"     [Cleaned]: {os.path.basename(target_path)}")
                    cleaned += 1
                else:
                    print_output("     [Already Clean]")
                    target_path = source_path
                    skipped += 1

                # Set ID3 tags when we can parse "Artist - Title"
                base_no_ext = os.path.splitext(os.path.basename(target_path))[0]
                if " - " in base_no_ext:
                    artist, title = base_no_ext.split(" - ", 1)
                    status = set_id3_tags(target_path, artist.strip(), title.strip())
                    if status == "ok":
                        print_output("     [Tags Set]")
                        tagged += 1
                    elif status == "unable":
                        print_output("     [Tags Skipped]")
                        unable_to_load += 1
                    else:  # "error"
                        print_output("     [Tags Skipped]")
                        errors += 1
                else:
                    print_output("     [Tags Skipped]")

            except Exception as e:
                errors += 1
                print_output(f"     [ERROR]: {e}")
                continue
    finally:
        # fold any mutagen warnings we caught into the Errors count
        errors += getattr(_h, "count", 0)
        mut_logger.removeHandler(_h)
        mut_logger.setLevel(_prev_level)
        mut_logger.propagate = _prev_propagate

    # Final summary line (renamed warning bucket)
    print_output(
        f"[INFO] Files Renamed {cleaned} | "
        f"Already Clean Files {skipped} | "
        f"Title/Artist Tagged {tagged} | "
        f"MP3 Tags Load Failures {unable_to_load} | "
        f"Errors {errors}"
    )