# AudioProgram v7.a

### A Python tool for organizing and enhancing your MP3 library  
**Status:** Final version (only minor bug fixes pending)  
**Python Version:** 3.8+

---

## About

AudioProgram v7.a is a powerful and user-friendly script designed to clean and organize MP3 files—particularly those downloaded from YouTube. It provides:

- Filename cleanup (removing site/video tags and unwanted characters)  
- ID3 tag editing (sets artist, album artist, and title metadata)  
- Interactive GUI input for custom folder paths and tag patterns  
- Safe renaming and tagging of all MP3 files in a specified folder  

**Warning:** This script directly modifies MP3 files. Please back up your music files before use.

---

## How to Use

1. Install Dependencies  
   Run the following command to install the required package:
   ```bash
   python3 -m pip install eyed3
   ```

2. Set Up the Program Folder  
   - Place `main.py` and the `AudioProgramV6` (or latest version folder) in the same directory.  
   - Ensure your MP3 files are in a folder you can reference during execution.

3. Run the Program  
   Launch the script using:
   ```bash
   python main.py
   ```

4. Follow the Prompts  
   - Input the folder path where your MP3 files are stored.  
   - Optionally provide additional website or video tags you'd like removed from filenames.  
   - Let the program process, tag, and rename your MP3s automatically.

---

## Features

- Custom Music Folder Input: Choose your MP3 directory via GUI prompt  
- Filename Normalization: Replaces underscores, strips unwanted tags (e.g. [Official Video], site names)  
- ID3 Tagging: Automatically parses artist/title from filenames and embeds metadata  
- Batch Processing: Processes all `.mp3` files within the target folder (including subfolders)  
- Interactive GUI Prompts: Uses `tkinter` for input dialogs (no command-line args needed)

---

## Dependencies

- eyed3: https://eyed3.readthedocs.io/en/latest/  
- Python standard libraries: os, tkinter, logging

---

## Configuration Notes

- Supports custom YouTube or website tags (e.g. "YouTube ", "[MV] ", "HD ") to be removed during cleanup.  
- Automatically skips read-only files to avoid crashing.  
- Keeps file extensions intact and applies changes only if needed.

---

## Project Status

Final Release (v7.a)  
Only bug fixes or minor improvements will be made in future patches.


dvanovcan@gmail.com

