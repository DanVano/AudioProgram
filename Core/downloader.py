import os
import re
import shutil

try:
    import yt_dlp
except ImportError:
    raise RuntimeError("yt-dlp is not installed. Run: pip install yt-dlp")

if not shutil.which("ffmpeg"):
    raise RuntimeError("FFmpeg not found on PATH. Run: winget install Gyan.FFmpeg")

from tag_cleaner import clean_filename, set_id3_tags, parse_shazam_csv
from utils import read_user_config, save_user_config


def _normalize(text):
    """Lowercase and strip punctuation for loose artist/title matching."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def build_music_database(music_folder):
    """
    Scan music_folder for MP3s and return a set of normalized 'artist title' keys.
    Reads filenames in 'Artist - Title.mp3' format, which is what this program produces.
    """
    db = set()
    if not os.path.isdir(music_folder):
        return db
    for fname in os.listdir(music_folder):
        if not fname.lower().endswith(".mp3"):
            continue
        stem = os.path.splitext(fname)[0]
        if " - " in stem:
            artist, title = stem.split(" - ", 1)
            db.add(_normalize(artist) + " " + _normalize(title))
    return db

def already_in_library(artist, title, db):
    """Return True if this artist+title already exists in the scanned music database."""
    return (_normalize(artist) + " " + _normalize(title)) in db

def download_track(artist, title, output_path):
    """
    Search YouTube for 'artist - title', download the best available audio,
    and convert to MP3 at the highest quality via FFmpeg.

    output_path must be the full path including the .mp3 extension.
    Raises RuntimeError on failure.

    Requires FFmpeg to be installed and on PATH for MP3 conversion.
    """
    query = f"ytsearch1:{artist} - {title}"
    # yt-dlp appends the extension itself, so strip .mp3 from the template
    stem = output_path[:-4] if output_path.lower().endswith(".mp3") else output_path

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "0",    # VBR best (~320kbps)
        }],
        "outtmpl": stem + ".%(ext)s",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "max_downloads": 1,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([query])
    except yt_dlp.utils.DownloadError as e:
        raise RuntimeError(f"yt-dlp: {e}")

    if not os.path.exists(output_path):
        raise RuntimeError(f"File not found after download — FFmpeg may not be installed: {output_path}")

    return output_path


def run_downloader(config, print_output, progress, root):
    from datetime import datetime
    print_output("\n[INFO] Running Shazam downloader...")

    try:
        entries = parse_shazam_csv(config["csv_path"], print_output)
        if not entries:
            print_output("[WARN] No valid entries found in CSV.")
            return

        progress["value"] = 0
        progress["maximum"] = len(entries)

        try:
            last_scanned_date = datetime.strptime(config["last_scanned_date"], "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            last_scanned_date = datetime.min

        library_folder = config.get("library_folder", "")
        staging_folder = config.get("staging_folder", "downloads")
        os.makedirs(staging_folder, exist_ok=True)

        music_db = build_music_database(library_folder)
        print_output(f"[INFO] Library scanned: {len(music_db)} existing tracks found.")
        print_output(f"[INFO] New downloads → {staging_folder}")

        count = 0
        skipped = 0
        newest_date = last_scanned_date
        entries = sorted(entries, key=lambda e: e["date"], reverse=True)

        for entry in entries:
            if entry["date"] <= last_scanned_date:
                break
            try:
                # Advance newest_date for every entry we process (skip or download)
                newest_date = max(newest_date, entry["date"])

                if already_in_library(entry["artist"], entry["title"], music_db):
                    print_output(f"[SKIP] Already in library: {entry['combined_track_info']}")
                    skipped += 1
                    progress["value"] += 1
                    continue

                raw_name = f"{entry['artist']} - {entry['title']}.mp3"
                output_name = clean_filename(raw_name, config.get("song_tags", []), config.get("web_tags", []))

                # uniquify filename if a collision exists in staging
                base, ext = os.path.splitext(output_name)
                candidate = output_name
                i = 2
                while os.path.exists(os.path.join(staging_folder, candidate)):
                    candidate = f"{base} ({i}){ext}"
                    i += 1
                output_name = candidate

                output_path = os.path.join(staging_folder, output_name)
                progress.pulse()
                try:
                    download_track(entry["artist"], entry["title"], output_path)
                finally:
                    progress.stop_pulse()
                print_output(f"[OK] Downloaded: {output_name}")

                set_id3_tags(output_path, entry["artist"], entry["title"], print_output)

                # keep db current so later duplicates in this run are also caught
                music_db.add(_normalize(entry["artist"]) + " " + _normalize(entry["title"]))

                count += 1

            except Exception as e:
                print_output(f"[ERROR] {entry['combined_track_info']}: {e}")

            progress["value"] += 1

        if newest_date > last_scanned_date:
            config["last_scanned_date"] = newest_date.strftime("%Y-%m-%dT%H:%M:%S")
            save_user_config(config)

        print_output(f"\n[INFO] Downloaded {count} | Already in Library {skipped}")
        progress["value"] = 0

    except Exception as e:
        print_output(f"[ERROR] Unexpected error: {e}")
