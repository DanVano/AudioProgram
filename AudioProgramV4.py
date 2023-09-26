            ### Downloaded MP3 files from youtube songname cleaner and metadata inputter
            ### Version 4


import os
import eyed3
import logging
logging.getLogger("eyed3.mp3.headers").setLevel(logging.CRITICAL)

print("""Welcome to the MP3 filename cleaner and ID3 metadata input program
       
                        """)

            ### Music Folder Directory

## Default Music folder
musicfolder = ('C:/Users/vanov/PythonPrograms/Music/musictest')
    
## Input custom music folder directory
mfinput = input("""Please enter your Music folder directory (x for default):
example: (C:/Users/vanov/PythonPrograms/Music/musictest)
:""")                
if 'x' == mfinput:
    musicfolder = ('C:/Users/vanov/PythonPrograms/Music/musictest')
else:
    musicfolder = mfinput
print('')
      
            ### Youtube song tags to remove from the filename

DLweb = ('[ytmp3.page] ', 'yt5s.io - ', '[YT2mp3.info] - ')
DLtags = [' (Lyric Video)', ' (Audio)', ' (Official Audio)', ' (Official Music Video)', ' (Lyrics)', ' (Official Video)', ' (Audio Only)', ' (Official Lyric Video)', 
            ' Official Video', ' (320 kbps)', ' (320kbps)', ' Official Lyric Video', ' (getmp3.pro)', ' [Lyrics]',  ' (Visualizer)']
songfile= []
NSF= songfile

            ### A function to insert and save Song files ID3 metadata

def songtagsave(songfile, NSF):
    ArtN = (NSF.split('-')[0])
    TtlN = (NSF.split('-')[-1])
    audiod3 = eyed3.load(f"{root}//{songfile}")
    audiod3.tag.artist = ArtN.rstrip()
    audiod3.tag.album_artist = ArtN.rstrip()
    audiod3.tag.title = (TtlN[:-4].strip())
    audiod3.tag.save()
    os.rename((f"{root}\\{songfile}"), (f"{root}\\{NSF}"))

            ### A function to print completed song info

def endprint(songfile, NSF):
    audiod3 = eyed3.load(f"{root}//{NSF}")
    print('vvv Song is fixed vvv')
    print('  Filename: ', NSF)
    print('  Artist: ', audiod3.tag.artist)
    print('  Title: ', audiod3.tag.title)

            ### A For loop to scan the Directory for Mp3 files and opens them

for root, dirs, files in os.walk(musicfolder):
    print('Searching for MP3 files within:')
    print(root)
    print('')
    for songfile in files:
        if songfile.endswith('.mp3'):
            NSF = songfile.replace('_', ' ').strip()
            if any([x in NSF for x in DLtags]) and any([x in NSF for x in DLweb]) and '-' in NSF:
                for remove in DLtags:
                    NSF = NSF.replace(remove, '')
                for remove in DLweb:
                    NSF = NSF.replace(remove, '')
                songtagsave(songfile, NSF)
                endprint(songfile, NSF)
            elif any([x in NSF for x in DLweb]) and '-' in NSF:
                for remove in DLweb:
                    NSF = NSF.replace(remove, '')
                songtagsave(songfile, NSF)
                endprint(songfile, NSF)
            elif any([x in NSF for x in DLtags]) and '-' in NSF:
                for remove in DLtags:
                    NSF = NSF.replace(remove, '')
                songtagsave(songfile, NSF)
                endprint(songfile, NSF)
            elif '-' in NSF:
                ArtN = (NSF.split('-')[0])
                TtlN = (NSF.split('-')[-1])
                songtagsave(songfile, NSF)
            else:
                audiod3 = eyed3.load(f"{root}//{songfile}")
                if audiod3.tag.artist is not None and audiod3.tag.title is None:
                    audiod3.tag.title = NSF[:-4].strip()
                    audiod3.tag.album_artist = audiod3.tag.artist
                    audiod3.tag.save()
                    os.rename((f"{root}\\{songfile}"), (f"{root}\\{NSF}"))
                    endprint(songfile, NSF) 
                elif audiod3.tag.title is None:
                    audiod3.tag.artist = NSF[:-4].strip()
                    audiod3.tag.album_artist = NSF[:-4].strip()
                    audiod3.tag.title = NSF[:-4].strip()
                    audiod3.tag.save()
                    os.rename((f"{root}\\{songfile}"), (f"{root}\\{NSF}"))
                    print('vvv Song is fixed vvv')
                    print('  Filename: ', NSF)
                    print('  Artist: None given, songname as placeholder')
                    print('  Title: ', audiod3.tag.title)
        else:
            print('Music naming program has completed. Updated ID3 metadata tags and the Filename ')
            print('')
    break
