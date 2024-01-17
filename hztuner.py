# -*- coding: utf-8 -*-

"""
Created on Fri Mar 31 19:23:15 2023

@author: Tj
@title: Song Tuner
@description:
A script that takes songs (assumed to be tuned to A440 Hz and converts to a solfeggio frequency.

ffmpeg -i "C:/Users/user/Music/Sabrina_Claudio/No Rain, No Flowers/08 - Messages From Her.mp3" -filter:a rubberband=pitch=0.9818181818181818 -y -acodec libmp3lame -b:a 256k "C:/Users/Tj/Music/test2.mp3"

Arguments explained: 
-i is the input file
-y = overwrite (no prompt)
-acodec use the 'libmp3lame' codec 
-b:a 256k audio bitrate 256 kbps

Frequencies (Scale Factors):

440->432 =  0.9818181818 (432/440)

622.25->639 = 1.02691844114 (639/622.25)
"""
import os
import sys
import ffmpy

# Make the song conversion function and use throughout the script
def songTune(songPath: str):
    #print(songPath)
    base, ext = os.path.splitext(songPath)
    appending_string = ' ({}Hz){}'.format(freq, ext)
    out_title = base + appending_string
    #print(base,'|' ,ext)
    #print(out_title)
    
    # .mp3 support
    if ext == '.mp3':
        ff=ffmpy.FFmpeg(
            inputs={songPath: None},
            outputs={os.path.splitext(songPath)[0] + appending_string: '-af "rubberband=pitch={}" -y -acodec libmp3lame -b:a 256k'.format(factor)})
    # .opus support
    elif ext == '.opus':
        ff=ffmpy.FFmpeg(
        inputs={songPath: None},
        outputs={os.path.splitext(songPath)[0] + appending_string: '-af "rubberband=pitch={}" -y -acodec libopus -b:a 128k'.format(factor)})
    # file not supported
    else:
        print("File type {} not supported".format(ext),'\n')
        return -1
        
    #print(ff.cmd)
    ff.run()


# get command-line arguments and set variables
args=sys.argv
path = args[1]
freq = args[2] # set scale factor later


# frequency handling
freqs=[432, 639] # accepted frequencies
try:
 numfreq = float(freq)
except:
  print("Error. Could not convert to a numbered type")
  exit(-1)
  
if numfreq not in freqs:
    raise Exception("Not an accepted frequency. Try any of the following: {}".format(freqs))
else:
   # calculate frequency factor
   if numfreq==432:
        factor = numfreq/440
   elif numfreq==639:
        factor = numfreq/622.25
#print(f'Calculated Factor = {factor}')


# Single-song conversion or albums?
single_song = os.path.splitext(path)[1]  #is the provided path a file or does it have an extension?
if single_song != '':
    songTune(path)
    
# Album conversion
else:
    album_paths = []

    for entry in os.listdir(path):
        dir_test= os.path.join(path, entry)
        if os.path.isdir(dir_test):
            album_paths.append(dir_test)
        # apply conversion to songs in the parent directory -> can convert entire albums
        else:
            songTune(dir_test)
    #print(album_paths)
    
# iterate over albums and songs
    """Assume ONLY Audio files are in these directories"""
    """Find a way to completely traverse a directory tree"""
    for album in album_paths:
        songs = os.listdir(album)
        for song in songs:
            song_path = os.path.join(album, song)
            # only pass files into converter
            if os.path.isfile(song_path):
                songTune(song_path) 
            else:
                continue
                
# Completion message                
print('\n',"Done!")
