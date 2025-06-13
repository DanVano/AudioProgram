import os

user_config_path = "user_config.txt"

def read_user_config():
    config = {
        "music_folder": "C:/Desktop/Music",
        "csv_path": "C:/Desktop/Music/shazam_library.csv",
        "song_tags": [
            " (Lyric Video)", " (Audio)", " (Official Audio)", " (Official Music Video)",
            " (Lyrics)", " (Official Video)", " (Audio Only)", " (Official Lyric Video)",
            " Official Video", " (320 kbps)", " (320kbps)", " Official Lyric Video",
            " (getmp3.pro)", " [Lyrics]", " (Visualizer)"
        ],
        "web_tags": ["[ytmp3.page] ", "yt5s.io - ", "[YT2mp3.info] - "],
        "last_scanned_date": "2025-03-10"
    }

    if os.path.exists(user_config_path):
        with open(user_config_path, "r", encoding="utf-8") as f:
            for line in f:
                if '=' in line:
                    key, val = line.strip().split("=", 1)
                    if key in ["song_tags", "web_tags"]:
                        config[key] = val.split("|") if val else []
                    else:
                        config[key] = val
    return config

def save_user_config(config):
    with open(user_config_path, "w", encoding="utf-8") as f:
        for key, val in config.items():
            if isinstance(val, list):
                val = "|".join(val)
            f.write(f"{key}={val}\n")

def update_user_config(config, key, new_value):
    if isinstance(config.get(key), list):
        if isinstance(new_value, str):
            config[key].append(new_value)
        elif isinstance(new_value, list):
            config[key].extend(new_value)
    else:
        config[key] = new_value
    save_user_config(config)
