"""MAIN CODE FOR RPI MUSIC VISUALIZER
Play any audio file and synchronize lights to the music

The timing of the lights turning on and off is based upon the frequency
response of the music being played.  A short segment of the music is
analyzed via FFT to get the frequency response across each defined
channel in the audio range.

FFT calculation can be CPU intensive and in some cases can adversely
affect playback of songs (especially if attempting to decode the song
as well, as is the case for an mp3).  For this reason, the FFT
calculations are cached after the first time a new song is played on a windows machine.
The values are cached in a pickle file in the song-pickle folder.  Subsequent requests to play the same song will use the
cached information and not recompute the FFT, thus reducing CPU
utilization dramatically and allowing for clear music playback of all
audio file types.
"""

import atexit
import os
from glob import glob
import time
import random
import pygame
import pickle
from song import Song
from hardware_controller import ShiftRegister


# functions ===
def generate_playlist():
    """generate a list of random songs"""
    directory = os.getcwd()
    # songs = glob(directory + '/songs/*.mp3')  # use this if reading mp3 files
    songs = glob(directory + '/songs/*.wav')  # use this if reading wav files
    random.shuffle(songs)
    
    return len(songs), songs


class Lightshow(object):
    """Lightshow class contains info about the current playback status of the song.
    User input will run event handlers above which can trigger methods in the lightshow object."""

    def __init__(self,
                 paused=False):

        self.paused = paused

        atexit.register(self.exit_function)

    def exit_function(self):
        """exit function"""
        print('in the exit_function method of the lightshow class...')
        # put code here to stop the lightshow

    def start_show(self, song):
        """Start the lightshow for a song that has been analyzed"""
        pygame.mixer.music.load(song)
        start = time.time()
        pygame.mixer.music.play()
        time.sleep(current_song.sleep_times[0])  # sleep until the first beat
        end = time.time()
        print('the time taken from playing the song to the first beat: {}'.format(end-start))
        for chunk in range(1, len(current_song.sleep_times)):
            # U1.readBitList(current_song.lightshow_data[chunk][0])
            # U2.readBitList(current_song.lightshow_data[chunk][1])
            # U3.readBitList(current_song.lightshow_data[chunk][2])
            # U4.readBitList(current_song.lightshow_data[chunk][3])
            print('f1: {}'.format(current_song.lightshow_data[chunk][0]))
            time.sleep(current_song.sleep_times[chunk] * 0.75)  # keep the lights on for 75% of the chunk time
            # U1.clear()
            # U2.clear()
            # U3.clear()
            # U4.clear()
            time.sleep(current_song.sleep_times[chunk] * 0.245)  # turn the lights off for ~25% of the chunk time


if __name__ == "__main__":  # run the following code if running main.py directly (not imported)

    lightshow = Lightshow()  # declare a lightshow object
    U1 = ShiftRegister(33, 35, 31, 37)  # declare the shift register objects (dataPin, serialClock, latchPin, outEnable)
    U2 = ShiftRegister(36, 32, 38, 40)
    U3 = ShiftRegister(11, 7, 13, 15)
    U4 = ShiftRegister(16, 12, 18, 22)
    playlist_len, playlist = generate_playlist()  # create a playlist from the songs in the current directory
    pygame.mixer.init()
    print('playlist length: {}'.format(playlist_len))
    for audio_file in playlist:
        song_title = audio_file.title().split('\\')[-1].split('.')[0]
        try:  # see if there is a pickle for this song already
            with open('./song_pickles/{}.pkl'.format(song_title), 'rb') as fp:
                current_song = pickle.load(fp)
                print('now playing: {}'.format(song_title))
        except FileNotFoundError:  # no pickle for this song
            print('no pickle for current song: {}'.format(song_title))
            current_song = Song(audio_file, song_title)  # create a song object

        lightshow.start_show(audio_file)
