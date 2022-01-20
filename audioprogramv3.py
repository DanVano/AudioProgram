import os
import eyed3

for root, dirs, files in os.walk("C:\\Users\\skftw\\Desktop\\Musictest"):
    for songfile in files:
        audiod3 = eyed3.load(f"{root}\\{songfile}")
        if audiod3.tag.album or audiod3.tag.artist == None:
            print(songfile)
            ArtN = (songfile.split('-')[0])
            AlbAN = (songfile.split('-')[0])
            TtlN = (songfile.split('-')[-1])
            TtlN2 = TtlN.lstrip()
            print(ArtN)
            print(TtlN2)
            print(TtlN2[:-4])
            audiod3 = eyed3.load(f"{root}\\{songfile}")
            print(audiod3.tag.album_artist)
            print(audiod3.tag.artist)
            audiod3.tag.artist = ArtN.rstrip()
            audiod3.tag.album_artist = AlbAN.rstrip()
            audiod3.tag.title = (TtlN2[:-4])
            audiod3.tag.save()
            OSN2 = (f"{root}\\{songfile}")
            NSN2 = (f"{root}\\{TtlN}")
            os.rename(OSN2, NSN2)
    print("End")
