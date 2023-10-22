   ### AudioProgramV4

# About
This python program was built to clean up MP3 file names downloaded from Youtube for better readability and Input song title, artist info, and album artist info into the files ID3 metadata for better reabability when using mobile music apps.

The script then prompts the user for their music folder directory and any custom website or YouTube tags they want to remove from their filenames.

It walks through the specified directory, checks each file to see if it’s an MP3 file, removes any specified tags from its filename, and calls songtagsave() to save the ID3 tags in the file and calls endprint() to print the file data for the user.

Also, please be aware that this script will rename your files and modify their ID3 tags in place. It’s recommended to back up your files before running this script to prevent any accidental data loss.

# How to use the program
Install pip package   python3 -m pip install eyeD3. 

Run the file. 

Input your Music folder directory or hit x for default 

Input any extra website tags and song name tags or hit x for default.

# Imports
Built by importing eyed3 from https://eyed3.readthedocs.io/en/latest/


# Project Status
Final verison

dvanovcan@gmail.com

