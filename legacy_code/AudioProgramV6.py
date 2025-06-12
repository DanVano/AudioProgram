       ### Downloaded MP3 files from youtube songname cleaner and metadata inputter
            ### Version 4

import os
import eyed3
import logging
import tkinter as tk

from tkinter import messagebox, simpledialog

logging.getLogger("eyed3.mp3.headers").setLevel(logging.CRITICAL)

# Input for custom music folder directory
def custom_music_folder(music_folder):
    music_folder_input = simpledialog.askstring("Input", "Please enter your Music folder directory.\n example: (C:/Users/vanov/PythonPrograms/Music/musictest)\n (x for default)")
    if music_folder_input is None:
        return "Cancelled"
    elif music_folder_input != 'x' and not '\\' in music_folder_input:
        music_folder = music_folder_input
    elif '\\' in music_folder_input:
        music_folder= music_folder_input.replace('\\','/')
    
    return music_folder

# User Input for custom Website tags and Youtube Tags removal
def custom_tags_removal(DLweb, DLtags):
    DLweb_input = simpledialog.askstring("Input", f"Input any custom Website tags you would like to remove\n Default= {DLweb}\n (x for default): ")
    if DLweb_input is None:
        return 
    elif DLweb_input != 'x':
        DLweb.append(DLweb_input + ' ')
    DLtags_input = simpledialog.askstring("Input", f"Input any custom Youtube song name tags you would like to remove\n (x for default): ")
    if DLtags_input is None:
        return "Cancelled"
    elif DLtags_input != 'x':
        DLtags.append(' ' + DLtags_input)
    return DLweb, DLtags   
           
# A function to insert and save Song files ID3 metadata
def songtagsave(old_mp3_name, new_mp3_name, root):
    audiod3 = eyed3.load(f"{root}//{old_mp3_name}")
    artist_name, song_title = new_mp3_name.rsplit('-', 1)
    audiod3.tag.artist = artist_name.rstrip()
    audiod3.tag.album_artist = song_title.rstrip()
    audiod3.tag.title = (song_title[:-4].strip())
    audiod3.tag.save()
    os.rename((f"{root}\\{old_mp3_name}"), (f"{root}\\{new_mp3_name}"))
    return audiod3.tag.artist, audiod3.tag.title

# Main loop to iterate over each file in the directory
def mp3_cleaner(music_folder, DLtags, DLweb):
    results = []
    old_mp3_name = []
    new_mp3_name = old_mp3_name
    # A For loop to scan the Directory for Mp3 files and opens them
    for root, _, files in os.walk(music_folder):
        results.append(f"Searching for MP3 files within:\n  {root}\n")
        # Process each file in the current root
        for old_mp3_name in [file for file in files if file.endswith('.mp3')]:
            new_mp3_name = old_mp3_name.replace('_', ' ').strip()
            # Check the song name for Website tags and Youtube tags. Remove if necessary
            if any(remove in new_mp3_name for remove in DLtags + DLweb) and '-' in new_mp3_name:
                for remove in DLtags + DLweb:
                    new_mp3_name = new_mp3_name.replace(remove, '')
                artist_name, song_title = songtagsave(old_mp3_name, new_mp3_name, root)
                results.append(f"Song: {new_mp3_name}\n  Artist: {artist_name}\n  Title: {song_title}\n")
            # Is the song name saved in Artist - Song name format
            elif '-' in new_mp3_name:
                artist_name, song_title = songtagsave(old_mp3_name, new_mp3_name, root)
                results.append(f"Song: {new_mp3_name}\n  Artist: {artist_name}\n  Title: {song_title}\n")
            # Just the individual Song name format
            else:
                audiod3 = eyed3.load(f"{root}//{old_mp3_name}")     
                # If Artist name found in metadata with only Songname as the file name
                if audiod3.tag.artist and not audiod3.tag.title:
                    audiod3.tag.title = new_mp3_name[:-4].strip()
                    audiod3.tag.save()
                    os.rename((f"{root}\\{old_mp3_name}"), (f"{root}\\{new_mp3_name}"))
                    results.append(f"Song: {new_mp3_name}\n  Artist: {audiod3.tag.artist}\n  Title: {audiod3.tag.title}\n")
                # Artist and Song Title metadata not found
                elif not audiod3.tag.title:
                    audiod3.tag.artist = new_mp3_name[:-4].strip()
                    audiod3.tag.album_artist = new_mp3_name[:-4].strip()
                    audiod3.tag.title = new_mp3_name[:-4].strip()
                    audiod3.tag.save()
                    os.rename((f"{root}\\{old_mp3_name}"), (f"{root}\\{new_mp3_name}"))
                    results.append(f"Song: {new_mp3_name}\n  Artist: None given, songname as placeholder\n  Title: {audiod3.tag.title}\n")  
                elif "_" in old_mp3_name:
                    # Metadata is fine. cleaned up Songname
                    os.rename((f"{root}\\{old_mp3_name}"), (f"{root}\\{new_mp3_name}"))
                    results.append(f"Song: {new_mp3_name} is Fixed!\n Just removed _ from the filename\n")  
        results.append('\nMusic naming program has completed. Updated ID3 metadata tags and the song Filenames.')
    return results
