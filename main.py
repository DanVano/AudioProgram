import tkinter as tk
from input_handler import update_and_show
from tag_cleaner import clean_filename, set_id3_tags, parse_shazam_csv
from downloader import download_youtube_audio, get_youtube_url_from_track
from utils import read_user_config, save_user_config

config = read_user_config()

root = tk.Tk()
root.title("MP3 Downloader GUI")
text_output = tk.Text(root, height=30, width=75)
text_output.pack()

# ========== ACTIONS ==========
def run_cleaner():
    text_output.insert(tk.END, "\nRunning cleaner...\n")
    # This is a placeholder: Normally, you'd loop through files in music_folder and clean filenames
    text_output.insert(tk.END, "(Cleaning simulation complete)\n")

def run_downloader():
    text_output.insert(tk.END, "\nRunning Shazam downloader...\n")
    entries = parse_shazam_csv(config["csv_path"])
    for entry in entries:
        if entry['date'] <= config["last_scanned_date"]:
            break
        yt_url = get_youtube_url_from_track(entry['artist'], entry['title'])
        output_name = clean_filename(f"{entry['artist']} - {entry['title']}.mp3", config["song_tags"], config["web_tags"])
        filepath = download_youtube_audio(yt_url, output_name)
        set_id3_tags(filepath, entry['artist'], entry['title'])
        text_output.insert(tk.END, f"Downloaded: {output_name}\n")
        config["last_scanned_date"] = entry['date']
    save_user_config(config)

# ========== MENU ==========
menu_items = [
    ("1. Run MP3 Cleaner", run_cleaner),
    ("2. Run Shazam Downloader", run_downloader),
    ("3. Set Music Folder", lambda: update_and_show(root, text_output, config, "music_folder", "music folder", ask_path=True)),
    ("4. Set CSV Path", lambda: update_and_show(root, text_output, config, "csv_path", "CSV path")),
    ("5. Set Song Tags", lambda: update_and_show(root, text_output, config, "song_tags", "song tags", is_list=True)),
    ("6. Set Web Tags", lambda: update_and_show(root, text_output, config, "web_tags", "web tags", is_list=True)),
    ("7. Exit", root.destroy)
]

for text, command in menu_items:
    tk.Button(root, text=text, command=command).pack()

text_output.insert(tk.END, f"Current Config:\nCSV: {config['csv_path']}\nTags: {config['song_tags']}\nWeb Tags: {config['web_tags']}\n")
root.mainloop()
