import tkinter as tk

from tkinter import messagebox, simpledialog

from AudioProgramV6 import *

# Default Music Folder Directory
#Song_File= []
#New_Song_File= Song_File
music_folder = ('C:/Users/vanov/PythonPrograms/Music/musictest')

### Default tags to remove from the song filename
DLweb = ['[ytmp3.page] ', 'yt5s.io - ', '[YT2mp3.info] - ']
DLtags = [' (Lyric Video)', ' (Audio)', ' (Official Audio)', ' (Official Music Video)', ' (Lyrics)', ' (Official Video)', ' (Audio Only)', ' (Official Lyric Video)', 
            ' Official Video', ' (320 kbps)', ' (320kbps)', ' Official Lyric Video', ' (getmp3.pro)', ' [Lyrics]',  ' (Visualizer)']
   
# The Main Menu choices for the User
def menu_selection(user_choice):
    global DLweb, DLtags, music_folder
    result_text.delete(1.0, tk.END)
    if user_choice == 1:
        results = mp3_cleaner(music_folder, DLtags, DLweb)
        if results == "Cancelled":
            return
        for result in results:
            result_text.insert(tk.END, f"{result}\n")
    elif user_choice == 2:
        DLweb, DLtags = custom_tags_removal(DLweb, DLtags)
        result = "Custom tags added"
        if result == "Cancelled":
            return
    elif user_choice == 3:
        music_folder = custom_music_folder(music_folder)
        result = "Custom music folder"
        if result == "Cancelled":
            return
    elif user_choice == 4:
        root.destroy()
        return
    else:
        result = 'Invalid choice. Please choose a valid option'
    result_text.insert(tk.END, f"{result}")

#The GUI for the Main Menu Options
root = tk.Tk()
root.title("Mp3 Cleaner")
main_menu_label = tk.Label(root, text="Main Menu\n", font=("Arial", 18))
main_menu_label.pack()
main_menu_info = tk.Label(root, text="Welcome to the MP3 Cleaner! This tool helps you enhance\n readability by removing YouTube and website tags from your\n filenames. Plus, it inputs Artist and Song names into metadata\n for iOS and Android music apps.\n", font=("Arial", 14))
main_menu_info.pack()
main_menu_hint = tk.Label(root, text="Press 1 to begin with default settings or first input option 2 and/or 3 before beginning the program\n", font=("Arial", 12))
main_menu_hint.pack()
menu_options = [
    "Begin Mp3 cleaner and metadata inputter",
    "Add custom tags to remove or input x for default",
    "Input your music folder or input x for default",
    "Quit"
    ]
for i, option in enumerate(menu_options, start=1):
    tk.Button(root, text=f"{i}. {option}", command=lambda value=i: menu_selection(value)).pack()

# Print results in GUI
result_label = tk.Label(root, text="\nResults", font=("Arial", 12))
result_label.pack()
result_text = tk.Text(root, height=30, width=72)
result_text.pack()
root.mainloop()
    
