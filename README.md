   ### AudioProgramV4
Final verison 
# About
This Python program is the final version, subject to potential minor tweaks in the future. It is a robust tool designed to enhance the organization and readability of your MP3 files, particularly those downloaded from YouTube. Here are the key features of this program:

File Renaming: The script improves the readability of your music library by cleaning up the filenames of your MP3 files. It removes any unwanted tags, such as those related to websites or YouTube, that may have been included in the filenames during download.

ID3 Tag Editing: The program inputs song title, artist information, and album artist details into the ID3 metadata of the files. This feature enhances the readability and organization of your music files when using mobile music apps.

User Customization: The script prompts users to input their music folder directory and any custom tags they wish to remove from their filenames. This allows for a personalized and efficient cleanup process.

Directory Walkthrough: The script traverses through the specified directory, identifies each MP3 file, and applies the cleanup and ID3 tag editing processes.

Data Presentation: After processing each file, the script calls an endprint() function to display the updated file data to the user. This allows users to review the changes made.

Please note that this script modifies your files directly by renaming them and altering their ID3 tags. To prevent accidental data loss, it’s recommended to back up your files before running this script.

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

