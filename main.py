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
import os, sys
from glob import glob
import time
import random
import pygame
import pickle
from song import Song
from hardware_controller import ShiftRegister

class Lightshow(object):
    """Lightshow class contains info about the current playback status of the song.
    User input will run event handlers above which can trigger methods in the lightshow object."""

    def __init__(self,
                 paused=False,
                 playlist=[],
                 song_index=0):

        self.paused = paused
        self.playlist = playlist
        self.song_index = song_index

        atexit.register(self.exit_function)
        Lightshow.generate_playlist()

    def generate_playlist(self):
        directory = os.getcwd()
        # songs = glob(directory + '/songs/*.mp3')  # use this if reading mp3 files
        self.playlist = glob(directory + '/songs/*.wav')  # use this if reading wav files
        random.shuffle(self.playlist)

    def next_song(self):
        print('play the next song')
        if self.song_index == len(self.playlist)-1:  # last song
            self.song_index = 0
        else:
            self.song_index += 1
        Lightshow.run(self.playlist[self.song_index])

    def prev_song(self):
        print('play previous song')
        if self.song_index > 1: # not the first song in the list
            self.song_index -= 1
        Lightshow.run(self.playlist[self.song_index])

    def pause_play(self):
        if self.paused:
            print('starting to play after being paused')
            pygame.mixer.music.play()
            self.paused = False
        else:
            print('pausing song...')
            pygame.mixer.music.pause()
            self.paused = True

    def exit_function(self):
        """exit function"""
        pygame.mixer.fadeout(1000)  # fade away the music for 1 second
        sys.exit

    def run(self, song):
        """Start the lightshow for a song that has been analyzed"""
        song_title = song.title().split('\\')[-1].split('.')[0]
        try:  # see if there is a pickle for this song already
            with open('./song_pickles/{}.pkl'.format(song_title), 'rb') as fp:
                current_song = pickle.load(fp)
        except FileNotFoundError:  # no pickle for this song
            print('no pickle for current song: {}'.format(song_title))
            Lightshow.next_song()
            # current_song = Song(audio_file, song_title)  # create a song object if running on a windows machine
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
    pygame.mixer.init()
    for audio_file in lightshow.playlist:
        lightshow.run(audio_file)
