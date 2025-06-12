import csv
import requests
import os
import eyed3  # For ID3 tagging

# ====================================
# 1) Parse Shazam CSV
# ====================================
def parse_shazam_csv(file_path):
    """
    Reads the CSV file at file_path and returns a list of dictionaries.
    Each dictionary has:
      'date'   -> TagTime (string YYYY-MM-DD)
      'artist' -> The Artist
      'title'  -> The Title
      'combined_track_info' -> "Artist - Title"
    """
    result = []
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f, fieldnames=["Index", "TagTime", "Title", "Artist", "URL", "TrackKey"])
        # If your CSV has a header row, remove this skip or adjust accordingly
        next(reader, None)  

        for row in reader:
            tag_time = row["TagTime"]  # e.g. "2025-03-10"
            artist = row["Artist"]
            title = row["Title"]
            combined = f"{artist} - {title}"

            result.append({
                'date': tag_time,
                'artist': artist,
                'title': title,
                'combined_track_info': combined
            })
    return result


# ====================================
# 2) Download from RapidAPI endpoint
#    and return full file path
# ====================================
def download_youtube_audio(api_key, youtube_url, output_filename="downloaded.mp3"):
    """
    Download the YouTube audio (mp3) using the provided RapidAPI service
    and return the local path to the downloaded file.
    """
    endpoint = "https://youtube-to-mp315.p.rapidapi.com/download"
    headers = {
        "X-RapidAPI-Host": "youtube-to-mp315.p.rapidapi.com",
        "X-RapidAPI-Key": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "url": youtube_url,
        "format": "mp3",
        "quality": 0
    }

    # 1) POST request to get the download link
    response = requests.post(endpoint, headers=headers, json=payload)
    if response.status_code != 200:
        raise RuntimeError(f"Request failed. Status: {response.status_code}, Body: {response.text}")
    resp_json = response.json()

    # 2) Extract the download link
    download_link = resp_json["progress"]["downloadLink"]

    # 3) Download the file from that link
    dl_response = requests.get(download_link, stream=True)
    if dl_response.status_code != 200:
        raise RuntimeError(f"File download failed. Status: {dl_response.status_code}")

    # 4) Save the file to your desired folder
    #    Adjust path as needed
    music_folder = r"C:\Users\YourUsername\Desktop\Music"
    os.makedirs(music_folder, exist_ok=True)

    file_path = os.path.join(music_folder, output_filename)
    with open(file_path, "wb") as f:
        for chunk in dl_response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    return file_path


# ====================================
# 3) ID3 Tagging with eyed3
# ====================================
def set_id3_tags(filepath, artist, title):
    """
    Loads the MP3 file at filepath using eyed3, then sets:
      - Artist
      - Album Artist
      - Title
    """
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


# ====================================
# 4) MAIN Program
#    - Load the last-scanned date from a text file
#    - Cycle Through CSV
#    - Stop if entry <= last-scanned date
#    - Download new entries as "Artist - Title.mp3"
#    - Set ID3 tags
#    - Save final last-scanned date
# ====================================
def main():
    # ----- CONFIG -----
    file_path = "shazam_library.csv"        # CSV path
    MY_API_KEY = "YOUR_API_KEY_HERE"       # RapidAPI key
    last_scanned_file = "Last_Scanned_Date.txt"

    # 1) Load last-scanned date if available; otherwise default
    if os.path.exists(last_scanned_file):
        with open(last_scanned_file, "r") as f:
            LAST_SCANNED_DATE = f.read().strip()
    else:
        LAST_SCANNED_DATE = "2025-03-10"

    # 2) Parse CSV
    data = parse_shazam_csv(file_path)
    newest_date_processed = LAST_SCANNED_DATE

    # 3) Loop over each entry in the CSV
    for entry in data:
        current_date = entry['date']

        # If we've reached old entries, stop processing
        if current_date <= LAST_SCANNED_DATE:
            print(f"Stopping because {current_date} <= last scanned date {LAST_SCANNED_DATE}")
            break

        # Suppose your CSV doesn't have direct YouTube URLs
        # You might generate them from artist/title or do a search:
        youtube_url = get_youtube_url_from_track(entry['artist'], entry['title'])

        # Build final filename: "Artist - Title.mp3"
        # e.g. "Daft Punk - One More Time.mp3"
        # It's best to remove any invalid filename characters as needed.
        output_file_name = f"{entry['artist']} - {entry['title']}.mp3"

        # 3a) Download the file
        downloaded_file_path = download_youtube_audio(
            api_key=MY_API_KEY,
            youtube_url=youtube_url,
            output_filename=output_file_name
        )

        # 3b) Set ID3 metadata
        set_id3_tags(downloaded_file_path, entry['artist'], entry['title'])

        # 3c) Print success
        print(f"Download complete = {entry['title']} - {entry['artist']}")

        # Update newest_date_processed so we know where we got to
        newest_date_processed = current_date

    # 4) Save the newest date we processed back to the text file
    with open(last_scanned_file, "w") as f:
        f.write(newest_date_processed)


# -------------------------------------
# Dummy function to demonstrate how to
# map "artist + title" -> YouTube URL.
# Replace with your own logic if needed.
# -------------------------------------
def get_youtube_url_from_track(artist, title):
    # For demonstration, returning a single test link
    return "https://www.youtube.com/watch?v=uHDyFWS_WjQ"


if __name__ == "__main__":
    main()
