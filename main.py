import tkinter as tk
from tkinter import messagebox
from input_handler import update_and_show
from tag_cleaner import clean_filename, set_id3_tags, parse_shazam_csv
from downloader import download_youtube_audio, get_youtube_url_from_track
from utils import read_user_config, save_user_config

config = read_user_config()

root = tk.Tk()
root.title("MP3 Downloader GUI")
text_output = tk.Text(root, height=30, width=75)
text_output.pack()

def print_output(msg):
    text_output.insert(tk.END, msg + "\n")
    text_output.see(tk.END)

# ========== ACTIONS ==========

def run_cleaner():
    print_output("\n[INFO] Running cleaner...")
    # Placeholder logic
    print_output("[INFO] Cleaner run complete (simulation)")

def run_downloader():
    print_output("\n[INFO] Running Shazam downloader...")

    try:
        entries = parse_shazam_csv(config["csv_path"])
        if not entries:
            print_output("[WARN] No valid entries found in CSV.")
            return

        count = 0
        for entry in entries:
            if entry['date'] <= config["last_scanned_date"]:
                break
            try:
                yt_url = get_youtube_url_from_track(entry['artist'], entry['title'])
                output_name = clean_filename(f"{entry['artist']} - {entry['title']}.mp3", config["song_tags"], config["web_tags"])
                filepath = download_youtube_audio(yt_url, output_name)
                set_id3_tags(filepath, entry['artist'], entry['title'])
                print_output(f"[OK] Downloaded: {output_name}")
                config["last_scanned_date"] = entry['date']
                count += 1
            except Exception as e:
                print_output(f"[ERROR] Failed to process track {entry['combined_track_info']}: {e}")

        if count > 0:
            save_user_config(config)
            print_output(f"[INFO] {count} new tracks downloaded.")
        else:
            print_output("[INFO] No new tracks to download.")
    except Exception as e:
        print_output(f"[ERROR] Unexpected error: {e}")
        messagebox.showerror("Error", f"Something went wrong during download:\n{e}")

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

print_output("Current Config:")
print_output(f"- CSV: {config.get('csv_path', '[Not Set]')}")
print_output(f"- Tags: {config.get('song_tags', [])}")
print_output(f"- Web Tags: {config.get('web_tags', [])}")
print_output(f"- Last Scanned: {config.get('last_scanned_date', '[Not Set]')}")

root.mainloop()
