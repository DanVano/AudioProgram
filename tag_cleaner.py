import eyed3
import os
from utils import read_user_config

def clean_filename(filename, song_tags, web_tags):
    for tag in song_tags + web_tags:
        filename = filename.replace(tag, "")
    return filename.strip()

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
    audio.tag.save()

def parse_shazam_csv(file_path):
    import csv
    result = []
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f, fieldnames=["Index", "TagTime", "Title", "Artist", "URL", "TrackKey"])
        next(reader, None)
        for row in reader:
            result.append({
                'date': row["TagTime"],
                'artist': row["Artist"],
                'title': row["Title"],
                'combined_track_info': f"{row['Artist']} - {row['Title']}"
            })
    return result
