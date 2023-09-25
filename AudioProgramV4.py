            ### Downloaded MP3 files from youtube songname cleaner and metadata inputter
            ### Version 4


import os
import eyed3
import logging
logging.getLogger("eyed3.mp3.headers").setLevel(logging.CRITICAL)

            ### Music Folder Directory

musicfolder = ('/Users/vanov/PythonPrograms/Music/musictest')

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
    OSN2 = (f"{root}\\{songfile}")
    NSN2 = (f"{root}\\{NSF}")
    os.rename(OSN2, NSN2)
                
            ### A For loop to scan the Directory for Mp3 files and opens them

for root, dirs, files in os.walk(musicfolder):
    print('   Searching for MP3 files within:', root)
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
                print('   The below Song is fixed')
                print(NSF)
            elif any([x in NSF for x in DLweb]) and '-' in NSF:
                for remove in DLweb:
                    NSF = NSF.replace(remove, '')
                songtagsave(songfile, NSF)
                print('   The below Song is fixed')
                print(NSF)
                #break
            elif any([x in NSF for x in DLtags]) and '-' in NSF:
                for remove in DLtags:
                    NSF = NSF.replace(remove, '')
                songtagsave(songfile, NSF)
                print('   The below Song is fixed')
                print(NSF)
                #break
            elif '-' in NSF:
                ArtN = (NSF.split('-')[0])
                TtlN = (NSF.split('-')[-1])
                songtagsave(songfile, NSF)
                print('   The below Song is fixed')
                print(NSF)
                #break
            else:
                audiod3 = eyed3.load(f"{root}//{songfile}")
                if audiod3.tag.artist is not None:
                    audiod3.tag.title = NSF[:-4]
                    audiod3.tag.album_artist = audiod3.tag.artist
                    audiod3.tag.save()
                    print('   The below Song is fixed')
                    print(NSF)
                else:
                    audiod3.tag.artist = NSF[:-4]
                    audiod3.tag.album_artist = NSF[:-4]
                    audiod3.tag.title = NSF[:-4]
                    audiod3.tag.save()
                    print('   The below Song is fixed')
                    print(NSF)
        else:
            print('Not a valid file format. Must be a MP3 file.')
    break
