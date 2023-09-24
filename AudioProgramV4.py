            ### Downloaded MP3 files from youtube songname cleaner and metadata inputter
            ### Version 4


import os
import eyed3
import logging
logging.getLogger("eyed3.mp3.headers").setLevel(logging.CRITICAL)

musicfolder = ('/Users/vanov/PythonPrograms/Music/musictest')
ytm = ('[ytmp3.page] ')
yt5 = ('yt5s.io - ')
yt2 = ('[YT2mp3.info] - ')
DLweb = (ytm, yt5, yt2)
DLtags = [' (Lyric Video)', ' (Audio)', ' (Official Audio)', ' (Official Music Video)', ' (Lyrics)', ' (Official Video)', ' (Audio Only)', ' (Official Lyric Video)', 
            ' Official Video', ' (320 kbps)', ' (320kbps)', ' Official Lyric Video', ' (getmp3.pro)', ' [Lyrics]',  ' (Visualizer)']
songfile= []
NSF= songfile

def songtagsave(songfile, NSF):
    ArtN = (NSF.split('-')[0])
    TtlN = (NSF.split('-')[-1])
    audiod3 = eyed3.load(f"{root}//{songfile}")
    audiod3.tag.artist = ArtN.rstrip()
    audiod3.tag.album_artist = ArtN.rstrip()
    audiod3.tag.title = (TtlN[:-4].strip())
    audiod3.tag.save()
    OSN2 = (f"{root}\\{songfile}")
    NSN2 = (f"{root}\\{NSF}")
    os.rename(OSN2, NSN2)
        

        #os.rename(OSN2, NSN2)
                
for root, dirs, files in os.walk(musicfolder):
    print('   Your Music Folder path:', root)
    print('')
    print('')
    for songfile in files:
        if songfile.endswith('.mp3'):
            NSF = songfile.replace('_', ' ')
            if any([x in NSF for x in DLtags]) and any([x in NSF for x in DLweb]) and '-' in NSF:    
                for remove in DLtags:
                    NSF = NSF.replace(remove, '')
                for remove in DLweb:
                    NSF = NSF.replace(remove, '')
                songtagsave(songfile, NSF)
                print('   Fixed the Song below')
                print(NSF)
            elif any([x in NSF for x in DLweb]) and '-' in NSF:
                for remove in DLweb:
                    NSF = NSF.replace(remove, '')
                songtagsave(songfile, NSF)
                print('   Fixed the Song below')
                print(NSF)
            elif any([x in NSF for x in DLtags]) and '-' in NSF:
                for remove in DLtags:
                    NSF = NSF.replace(remove, '')
                songtagsave(songfile, NSF)
                print('   Fixed the Song below')
                print(NSF)
            elif '-' in NSF:
                ArtN = (NSF.split('-')[0])
                TtlN = (NSF.split('-')[-1])
                songtagsave(songfile, NSF)
                print('   Fixed the Song below')
                print(NSF)
            else:
                audiod3 = eyed3.load(f"{root}//{songfile}")
                audiod3.tag.artist = NSF.strip()
                audiod3.tag.album_artist = NSF.strip()
                audiod3.tag.title = NSF.strip()
                print('   Fixed the Song below')
                print(NSF)
        else:
            print('Not a valid file format. Must be a MP3 file.')
    break
