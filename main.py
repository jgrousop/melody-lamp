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
        
        self.generate_playlist()

    def generate_playlist(self):
        directory = os.getcwd()
        self.playlist = glob(directory + '/songs/*.{}'.format(self.music_filetype))
        random.shuffle(self.playlist)

    def run(self, song):
        """Start the lightshow for a song that has been analyzed"""
        global paused
        global next_song
        global prev_song

        self.current_song_title = song.title().split('/')[-1].split('.')[0]

        try:  # see if there is a pickle for this song already
            with open('./song_pickles/{}.pkl'.format(self.current_song_title), 'rb') as fp:
                self.current_song = pickle.load(fp)
        except FileNotFoundError:  # no pickle for this song
            print('no pickle for current song: {}'.format(self.current_song_title))
            Lightshow.go_next()  # move on to the next song if a pickle hasn't been generated yet
            
        # start omxplayer to hear the music
        omxprocess = subprocess.Popen(['omxplayer','-o','local','/home/pi/lightshow/songs/{}.wav'.format(self.current_song_title)],
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                bufsize=0,
                                close_fds=True)

        sleep(self.current_song.sleep_times[0])  # sleep until the first beat
        
        for chunk in range(1, len(self.current_song.sleep_times)):
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

            if paused: # the user has pressed the pause button
                omxprocess.stdin.write(b'p')
                while paused:
                    sleep(0.25)  # keep waiting until the user presses the pause button again

            elif next_song: # the user has pressed the next_song button
                next_song = False
                omxprocess.stdin.write(b'q')  # quit the current music playback process
                if self.song_index < len(self.playlist):
                    self.song_index += 1 # go back to the first song if next is pressed on the last song
                self.run(self.playlist[self.song_index])

            elif prev_song: # the user has pressed the prev_song button
                prev_song = False
                omxprocess.stdin.write(b'q')  # quit the current music playback process
                if self.song_index > 0:
                    self.song_index -= 1
                self.run(self.playlist[self.song_index])
                    

if __name__ == "__main__":  # run the following code if running main.py directly
    GPIO.setmode(GPIO.BOARD)  # RPi.GPIO only works on the Raspberry Pi.
    GPIO.setwarnings(False)
    raspberry = Pi()  
    lightshow = Lightshow()
    U1 = ShiftRegister(33, 31, 35, 37)  # declare the shift register objects (dataPin, serialClock, latchPin, outEnable)
    U2 = ShiftRegister(38, 36, 40, 32)
    U3 = ShiftRegister(11, 13, 7, 15)
    U4 = ShiftRegister(18, 22, 16, 12)

    # for audio_file in lightshow.playlist:
    #     lightshow.run(audio_file)
