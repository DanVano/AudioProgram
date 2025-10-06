import os
import requests

from tag_cleaner import clean_filename, set_id3_tags
from utils import read_user_config, save_user_config

config = read_user_config()
rapidapi_key = config.get("rapidapi_key", "")
if not rapidapi_key:
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Configuration Error", "Missing RapidAPI key in user_config.txt.\n\nPlease add your key and restart the program.")
        root.destroy()
    except Exception:
        pass
    raise RuntimeError("Missing RapidAPI key in user_config.txt")

def download_youtube_audio(youtube_url, output_filename="downloaded.mp3"):
    endpoint = "https://youtube-to-mp315.p.rapidapi.com/download"
    headers = {
        "X-RapidAPI-Host": "youtube-to-mp315.p.rapidapi.com",
        "X-RapidAPI-Key": rapidapi_key,
        "Content-Type": "application/json"
    }
    payload = {
        "url": youtube_url,
        "format": "mp3",
        "quality": 0
    }

    try:
        response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to get download link: {e}")

    try:
        resp_json = response.json()
        download_link = resp_json["progress"]["downloadLink"]
    except (KeyError, ValueError) as e:
        raise RuntimeError(f"Unexpected response structure: {e}")

    config = read_user_config()
    music_folder = config.get("music_folder", "downloads")
    os.makedirs(music_folder, exist_ok=True)
    file_path = os.path.join(music_folder, output_filename)

    try:
        dl_response = requests.get(download_link, stream=True, timeout=60)
        dl_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"File download failed: {e}")

    try:
        with open(file_path, "wb") as f:
            for chunk in dl_response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    except IOError as e:
        raise RuntimeError(f"Failed to write file: {e}")

    return file_path

def get_youtube_url_from_track(artist, title):
    # Replace with real YouTube search logic as needed
    return "https://www.youtube.com/watch?v=uHDyFWS_WjQ"

def run_downloader(config, print_output, progress, root):
    from tag_cleaner import parse_shazam_csv
    from datetime import datetime
    print_output("\n[INFO] Running Shazam downloader...")

    try:
        entries = parse_shazam_csv(config["csv_path"])
        if not entries:
            print_output("[WARN] No valid entries found in CSV.")
            return

        progress["value"] = 0
        progress["maximum"] = len(entries)

        try:
            last_scanned_date = datetime.strptime(config["last_scanned_date"], "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            last_scanned_date = datetime.min
            
        count = 0
        entries = sorted(entries, key=lambda e: e['date'], reverse=True)
        for entry in entries:
            if entry['date'] <= last_scanned_date:
                break
            try:
                yt_url = get_youtube_url_from_track(entry['artist'], entry['title'])

                # build a target name like "Artist - Title.mp3" and clean it
                raw_name = f"{entry['artist']} - {entry['title']}.mp3"
                output_name = clean_filename(raw_name, config.get("song_tags", []), config.get("web_tags", []))

                # avoid accidental overwrite by uniquifying if needed
                music_folder = config.get("music_folder", "downloads")
                os.makedirs(music_folder, exist_ok=True)
                base, ext = os.path.splitext(output_name)
                candidate = output_name
                i = 2
                while os.path.exists(os.path.join(music_folder, candidate)):
                    candidate = f"{base} ({i}){ext}"
                    i += 1
                output_name = candidate

                filepath = download_youtube_audio(yt_url, output_name)
                print_output(f"[OK] Downloaded: {output_name}")

                # write ID3 tags from the parsed artist/title
                set_id3_tags(filepath, entry['artist'], entry['title'])

                last_scanned_date = entry['date']
                config["last_scanned_date"] = last_scanned_date.strftime("%Y-%m-%dT%H:%M:%S")
                count += 1
            except Exception as e:
                print_output(f"[ERROR] Failed to process track {entry['combined_track_info']}: {e}")

        if count > 0:
            save_user_config(config)
            print_output(f"[INFO] {count} new tracks downloaded.")
        else:
            print_output("[INFO] No new tracks to download.")

        progress["value"] = 0  # Reset after all done

    except Exception as e:
        print_output(f"[ERROR] Unexpected error: {e}")
        messagebox = __import__('tkinter').messagebox
        messagebox.showerror("Error", f"Something went wrong during download:\n{e}")
