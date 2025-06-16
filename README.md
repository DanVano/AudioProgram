# AudioProgram v8.0  
**A Python tool to organize, tag, and download MP3s with a simple GUI**

---

## Status
**Final release** (minor bug fixes only)  
**Python Version:** 3.8+

---

## About

AudioProgram v8.0 is a streamlined, GUI-based tool for downloading and cleaning MP3s, especially those sourced via Shazam or YouTube. It provides:

- MP3 filename cleanup (removes tags like `[Official Video]`)
- Batch ID3 tagging (artist, album artist, title)
- One-click YouTube download via Shazam CSV
- GUI-based input for paths, tag lists, and options

> **WARNING:** This tool modifies MP3 files. Back up your library before use.

---

## Folder Organization

```
/AudioProgram/
│
├── Core/                # All core Python .py files
│    ├── main.py
│    ├── downloader.py
│    ├── input_handler.py
│    ├── tag_cleaner.py
│    ├── utils.py
│    └── (other modules)
│
├── Config/              # User configuration files
│    └── user_config.txt
│
├── Setup_Scripts/       # Batch scripts for setup and launching
│    ├── install_setup.bat
│    └── run_audio_program.bat
│
├── requirements.txt     # Dependencies
├── README.md            # This file
└── (You may keep your shazam_library.csv wherever you want)
```

---

## How to Use

1. **Install Dependencies:**
   ```
   pip install eyed3 requests
   ```

2. **Set Up:**
    - All core `.py` files are located in the `/Core/` folder.
    - The configuration file (`user_config.txt`) is located in `/Config/`.
    - Batch scripts (`install_setup.bat`, `run_audio_program.bat`) are in `/Setup_Scripts/`.
    - Place your `shazam_library.csv` **anywhere you like** (such as your Desktop or Downloads). Set its location using the program’s GUI.

3. **Run the Program:**
    - From the project root, run:
      ```
      python Core/main.py
      ```
    - Or use the batch script:
      ```
      Setup_Scripts\run_audio_program.bat
      ```

4. **Use the GUI to:**
    - Download MP3s from a Shazam CSV
    - Clean filenames and apply tags
    - Set or update folder and tag values

---

## Features

- **YouTube Downloader:** Uses RapidAPI to fetch MP3s from YouTube
- **ID3 Tagging:** Automatically tags downloaded files
- **Cleaner:** Removes unwanted site/video tags from filenames
- **Persistent Config:** Remembers paths, tags, and last download date
- **GUI:** No command-line arguments required

---

## Dependencies

- [eyed3](https://eyed3.readthedocs.io/)
- Python libraries: `os`, `tkinter`, `csv`, `requests`

---

## Configuration

**Example user_config.txt (now in `/Config/`):**
```
rapidapi_key=YOUR_API_KEY
music_folder=C:/Music
csv_path=C:/Users/YourName/Desktop/shazam_library.csv
song_tags=(Lyrics)|(Official Video)
web_tags=[ytmp3.page] |yt5s.io -
last_scanned_date=2025-03-10T00:00:00
```

---

## Project Status

Final Release (v8.0).  
Actively maintained for bug fixes and small improvements only.
