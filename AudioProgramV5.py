       ### Downloaded MP3 files from youtube songname cleaner and metadata inputter
            ### Version 4


import os
import eyed3
import logging
logging.getLogger("eyed3.mp3.headers").setLevel(logging.CRITICAL)

### A function to insert and save Song files ID3 metadata

def songtagsave(SongFile, NewSongFile):
    ArtistName, SongTitle = NewSongFile.rsplit('-', 1)
    audiod3 = eyed3.load(f"{root}//{SongFile}")
    audiod3.tag.artist = ArtistName.rstrip()
    audiod3.tag.album_artist = ArtistName.rstrip()
    audiod3.tag.title = (SongTitle[:-4].strip())
    audiod3.tag.save()
    os.rename((f"{root}\\{SongFile}"), (f"{root}\\{NewSongFile}"))
    pass

### A function to print completed song info

def endprint(SongFile, NewSongFile):
    audiod3 = eyed3.load(f"{root}//{NewSongFile}")
    print('### Song is Fixed! >>>' , NewSongFile)
    print(' Artist: ', audiod3.tag.artist)
    print(' Title: ', audiod3.tag.title)
    pass

### Start of program ###

SongFile= []
NewSongFile= SongFile

print("""Welcome to the MP3 filename cleaner and ID3 metadata input program.
With this program you can remove Youtube tags and Website tags from your filename
for greater readability and input Artist and Song name into the metadata for IOS
and Andriod music apps.
      """)

### Music Folder Directory ###

### Default Music folder
musicfolder = ('C:/Users/vanov/PythonPrograms/Music/musictest')

### Input for custom music folder directory
mf_input = input("""Please enter your Music folder directory.
example: (C:/Users/vanov/PythonPrograms/Music/musictest)
(x for default)                
:""")                
if mf_input != 'x' and not '\\' in mf_input:
    musicfolder = mf_input
elif '\\' in mf_input:
    musicfolder= mf_input.replace('\\','/')
    print(musicfolder, 'replaced')    
print('')
      
### Default tags to remove from the song filename
DLweb = ['[ytmp3.page] ', 'yt5s.io - ', '[YT2mp3.info] - ']
DLtags = [' (Lyric Video)', ' (Audio)', ' (Official Audio)', ' (Official Music Video)', ' (Lyrics)', ' (Official Video)', ' (Audio Only)', ' (Official Lyric Video)', 
            ' Official Video', ' (320 kbps)', ' (320kbps)', ' Official Lyric Video', ' (getmp3.pro)', ' [Lyrics]',  ' (Visualizer)']

### Input for custom Website tags and Youtube Tags
DLweb_input = input("""Input any custom Website tags you would like to remove.                    
Defaults = [ytmp3.page], yt5s.io -, [YT2mp3.info] -)     
(x for default)                
:""")
if DLweb_input != 'x':
    DLweb.append(DLweb_input + ' ')
print('')
DLtags_input = input("""Input any custom Youtube song name tags you would like to remove.    
(x for default)                
:""")
if DLtags_input != 'x':
    DLtags.append(' ' + DLtags_input)
print('')

### A For loop to scan the Directory for Mp3 files and opens them
for root, dirs, files in os.walk(musicfolder):
    print('Searching for MP3 files within:')
    print(root)
    print('')
    ### Procces each file in the current root
    for SongFile in files:
        if SongFile.endswith('.mp3'):
            NewSongFile = SongFile.replace('_', ' ').strip()
            ### Check the song name for Website tags and Youtube tags. Remove if neccessary
            if any(x in NewSongFile for x in DLtags + DLweb) and '-' in NewSongFile:
                for remove in DLtags + DLweb:
                    NewSongFile = NewSongFile.replace(remove, '')
                songtagsave(SongFile, NewSongFile)
                endprint(SongFile, NewSongFile)
            ### Is the song name saved in Artist - Songname format
            elif '-' in NewSongFile:
                ArtistName, SongTitle = NewSongFile.rsplit('-', 1)
                songtagsave(SongFile, NewSongFile)
            ### just songname format
            else:
                audiod3 = eyed3.load(f"{root}//{SongFile}")
                ### If Artist name found in metadata with only Songname as the file name
                if audiod3.tag.artist is not None and audiod3.tag.title is None:
                    audiod3.tag.title = NewSongFile[:-4].strip()
                    audiod3.tag.album_artist = audiod3.tag.artist
                    audiod3.tag.save()
                    os.rename((f"{root}\\{SongFile}"), (f"{root}\\{NewSongFile}"))
                    endprint(SongFile, NewSongFile)
                ### Artist and Song Title metadata not found
                elif audiod3.tag.title is None:
                    audiod3.tag.artist = NewSongFile[:-4].strip()
                    audiod3.tag.album_artist = NewSongFile[:-4].strip()
                    audiod3.tag.title = NewSongFile[:-4].strip()
                    audiod3.tag.save()
                    os.rename((f"{root}\\{SongFile}"), (f"{root}\\{NewSongFile}"))
                    print('### Song is Fixed! >>>' , NewSongFile)
                    print(' Artist: None given, songname as placeholder')
                    print(' Title: ', audiod3.tag.title)
                elif "_" in SongFile:
                    ### Metadata is fine. cleaned up Songname
                    print('### Song is Fixed! >>>' , NewSongFile)
                    print(' Just removed _ from the filename')
                    os.rename((f"{root}\\{SongFile}"), (f"{root}\\{NewSongFile}"))
        else:
            print('File below is not a MP3')
            print(SongFile)
            print('')
    print('')
    print('Music naming program has completed. Updated ID3 metadata tags and the song Filenames.')
    print('End')
    print('')
    break