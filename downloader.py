import requests
import os
from config import rapidapi_key
from utils import read_user_config, save_user_config

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
    return "https://www.youtube.com/watch?v=uHDyFWS_WjQ"
