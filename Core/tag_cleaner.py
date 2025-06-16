import os
from datetime import datetime

import eyed3

from core.utils import read_user_config


def clean_filename(filename, song_tags, web_tags):
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
