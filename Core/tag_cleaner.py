import os
from datetime import datetime

import eyed3

from utils import read_user_config

def clean_filename(filename, song_tags, web_tags):
    # Replace underscores with spaces
    filename = filename.replace("_", " ")
    for tag in song_tags + web_tags:
        filename = filename.replace(tag, "")
    filename = filename.strip().strip("-").strip()
    if not filename.endswith(".mp3"):
        filename += ".mp3"
    return filename

def set_id3_tags(filepath, artist, title):
    audio = eyed3.load(filepath)
    if audio is None:
        print(f"Warning: Could not load file: {filepath}. ID3 tags not set.")
        return
    if audio.tag is None:
        audio.initTag()
    audio.tag.artist = artist
    audio.tag.album_artist = artist
    audio.tag.title = title
    try:
        audio.tag.save()
    except PermissionError:
        print(f"Permission denied: {filepath} is read-only.")
    except Exception as e:
        print(f"Error saving ID3 tags to {filepath}: {e}")

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
    print_output("\n[INFO] Running MP3 filename cleaner...")
    music_folder = config.get("music_folder", "")
    if not music_folder or not os.path.isdir(music_folder):
        print_output(f"[ERROR] Music folder not set or does not exist: {music_folder}")
        return

    files = [f for f in os.listdir(music_folder) if f.lower().endswith(".mp3")]
    if not files:
        print_output("[INFO] No MP3 files found in the selected folder.")
        return

    cleaned = 0
    skipped = 0
    for filename in files:
        original_path = os.path.join(music_folder, filename)
        cleaned_name = clean_filename(filename, config.get("song_tags", []), config.get("web_tags", []))
        cleaned_path = os.path.join(music_folder, cleaned_name)

        if os.path.exists(cleaned_path) and original_path != cleaned_path:
            print_output(f"[WARN] Skipping {filename}: target filename exists.")
            skipped += 1
            continue

        try:
            if original_path != cleaned_path:
                os.rename(original_path, cleaned_path)
                print_output(f"[OK] Renamed: {filename}  →  {cleaned_name}")
                cleaned += 1
            else:
                print_output(f"[OK] Already Clean: {filename}")

            # Parse artist and title from cleaned filename (expects "Artist - Title.mp3")
            base = os.path.splitext(cleaned_name)[0]
            if " - " in base:
                artist, title = base.split(" - ", 1)
                set_id3_tags(cleaned_path, artist.strip(), title.strip())
                print_output(f"[OK] Set ID3 tags for: {cleaned_name}")
            else:
                print_output(f"[WARN] Could not parse artist/title from filename: {cleaned_name}")

        except Exception as e:
            print_output(f"[ERROR] Failed to process {filename}: {e}")
            skipped += 1

    print_output(f"[INFO] Cleaned {cleaned} files. Skipped {skipped} files.\n")
