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
    
    response = requests.post(endpoint, headers=headers, json=payload)
    if response.status_code != 200:
        raise RuntimeError(f"Request failed. Status: {response.status_code}, Body: {response.text}")
    resp_json = response.json()

    download_link = resp_json["progress"]["downloadLink"]

    config = read_user_config()
    music_folder = config["music_folder"]
    os.makedirs(music_folder, exist_ok=True)

    file_path = os.path.join(music_folder, output_filename)
    dl_response = requests.get(download_link, stream=True)
    if dl_response.status_code != 200:
        raise RuntimeError(f"File download failed. Status: {dl_response.status_code}")

    with open(file_path, "wb") as f:
        for chunk in dl_response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    return file_path

def get_youtube_url_from_track(artist, title):
    return "https://www.youtube.com/watch?v=uHDyFWS_WjQ"
