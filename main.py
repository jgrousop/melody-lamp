"""
RPI MELODY LAMP =-=-
JOHN GROUSOPOULOS =-=-
Play any audio file and synchronize lights to the music

The timing of the lights turning on and off is based upon the frequency
response of the music being played.  A short segment of the music is
analyzed via FFT to get the frequency response across each defined
channel in the audio range.

FFT calculation can be CPU intensive and in some cases can adversely
affect playback of songs (especially if attempting to decode the song
as well, as is the case for an mp3).  For this reason, the FFT
calculations are cached after the first time a new song is played on a windows machine.
The values are cached in a pickle file in the song-pickle folder.  Subsequent requests 
to play the same song will use the cached information and not recompute the FFT, 
thus reducing CPU use dramatically and allowing for clear music playback of all audio file types.

NOTES =-=-=-=-
- edit the raspberry pi crontab by opening a terminal and typing crontab -e then enter the following
at the end of the file:
@reboot /usr/bin/python3 /home/pi/lightshow/main.py 
"""

import subprocess
from time import sleep
import os
from glob import glob
import random
import pickle
from hardware_controller import *
from song import Song
from gpiozero import Button


class Lightshow(object):
    """Lightshow class contains info about the current playback status of the song.
    User input will run event handlers which update global variables to control the show."""

    def __init__(self,
                 playlist=[],
                 song_index=0):

        self.playlist = playlist
        self.song_index = song_index
        self.current_song = None
        self.current_song_title = ''
        self.music_filetype = 'wav'
        self.paused = False
        self.next_pin = 23
        self.next_button = None
        self.prev_pin = 19
        self.prev_button = None
        self.pause_pin = 21
        self.pause_button = None
        self.omxprocess = None
        
        self.setup()
        self.generate_playlist()
        
    
    def setup(self):
        """create event detect on input pins for button presses"""
        self.next_button = Button(self.next_pin, pull_up=False, bounce_time=1)
        self.next_button.when_pressed = self.go_next
        self.prev_button = Button(self.prev_pin, pull_up=False, bounce_time=1)
        self.prev_button.when_pressed = self.go_prev
        self.pause_button = Button(self.pause_pin, pull_up=False, bounce_time=1)
        self.pause_button.when_pressed = self.pause_play
        
    def go_next(self):
        print('GO NEXT!')
        if self.song_index < len(self.playlist):
            self.song_index += 1 
        else:
            self.song_index = 0
        self.run(self.playlist[self.song_index])
        
    def go_prev(self):
        print('GO PREV!')
        self.omxprocess.stdin.write(b'q')  # quit the current music playback process
        if self.song_index > 0:
            self.song_index -= 1
        self.run(self.playlist[self.song_index])
        
    def pause_play(self):
        self.paused = not self.paused
        self.omxprocess.stdin.write(b'p')
        if self.paused: self.pause_button.wait_for_press() # see if this stops the lights with the music


    def generate_playlist(self):
        directory = os.getcwd()
        self.playlist = glob(directory + '/songs/*.{}'.format(self.music_filetype))
        random.shuffle(self.playlist)
        
        self.run(self.playlist[self.song_index])

    def run(self, song):
        """Start the lightshow for a song that has been analyzed"""
        
        self.current_song_title = song.title().split('/')[-1].split('.')[0]

        try:  # see if there is a pickle for this song already
            with open('./song_pickles/{}.pkl'.format(self.current_song_title), 'rb') as fp:
                self.current_song = pickle.load(fp)
        except FileNotFoundError:  # no pickle for this song
            print('no pickle for current song: {}'.format(self.current_song_title))
            self.call_next(1)  # move on to the next song if a pickle hasn't been generated yet
            
        # start omxplayer to hear the music
        self.omxprocess = subprocess.Popen(['omxplayer','-o','local','/home/pi/lightshow/songs/{}.wav'.format(self.current_song_title)],
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                bufsize=0,
                                close_fds=True)

        sleep(self.current_song.sleep_times[0])  # sleep until the first beat
        
        for chunk in range(len(self.current_song.sleep_times)):
            U1.readBitList(self.current_song.lightshow_data[chunk][0])
            U2.readBitList(self.current_song.lightshow_data[chunk][1])
            U3.readBitList(self.current_song.lightshow_data[chunk][2])
            U4.readBitList(self.current_song.lightshow_data[chunk][3])
            sleep(self.current_song.sleep_times[chunk] * 0.75)  # keep the lights on for 75% of the chunk time
            U1.clear()
            U2.clear()
            U3.clear()
            U4.clear()
            sleep(self.current_song.sleep_times[chunk] * 0.245)  # turn the lights off for ~25% of the chunk time
        
        self.song_index += 1
        if self.song_index <= len(self.playlist):
            self.run(self.playlist[self.song_index]) # play the next song
        else:
            self.generate_playlist() # re-start from the beginning with a newly randomized list of songs


if __name__ == "__main__":  # run the following code if running main.py directly
    
    U1 = ShiftRegister(33, 31, 35, 37)  # declare the shift register objects (dataPin, serialClock, latchPin, outEnable)
    U2 = ShiftRegister(38, 36, 40, 32)
    U3 = ShiftRegister(11, 13, 7, 15)
    U4 = ShiftRegister(18, 22, 16, 12)

    lightshow = Lightshow()