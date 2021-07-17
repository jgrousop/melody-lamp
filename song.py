"""
Song information to be saved and loaded from pickle files.
"""

import os
import pickle
import statistics
from glob import glob
import librosa as lr
import matplotlib.pyplot as plt
from pydub import AudioSegment
import numpy as np


class Song(object):
    def __init__(self,
                 file=None,
                 title='',
                 timestamps=[],
                 sleep_times=[],
                 volumes=[],
                 length=0.0,
                 sample_rate=22050,
                 tempo=0.0,
                 num_chunks=0,
                 freq_bins=[0, 110, 410, 700, 20000],
                 lightshow_data=None):

        self.file = file  # song file where the data will be pulled from
        self.title = title  # song title
        self.timestamps = timestamps
        self.sleep_times = sleep_times
        self.volumes = volumes  # maximum volume for each time chunk
        self.length = length  # song length in [s]
        self.sample_rate = sample_rate  # how many data points of audio data per second of audio length
        self.tempo = tempo  # song tempo in [bpm]
        self.num_chunks = num_chunks  # how many chunks the song is broken into for frequency analysis
        self.freq_bins = freq_bins  # upper cutoffs of frequency bins [Hz]
        self.lightshow_data = lightshow_data  # 
        self.amplitude_data = None

        #self.check_extension()
        self.generate_pickle()

    def generate_pickle(self):
        """
        open a pickle of the song data or create one if it doesn't exist.
        """

        self.compute_amplitude()  # obtain time series data
        self.beat_tracking()  # determine beat locations
        self.compute_lightshow_data()  # determine binary lists for shift registers
        # disp_song_data = input('plot song data? [Y/N]:   ')
        # if 'Y' in disp_song_data or 'y' in disp_song_data:
        #     self.plot_song_data()

        with open('./song_pickles/{}.pkl'.format(self.title), 'wb') as output:
            pickle.dump(self, output, protocol=4)

    def compute_amplitude(self):
        self.amplitude_data, self.sample_rate = lr.load(self.file)  # time series amplitude data and sample frequency
        self.length = len(self.amplitude_data) / self.sample_rate  # length of song in seconds

    def beat_tracking(self):
        """
        calculate the tempo for the song and use the float value to re-calculate the chunk size.
        Timestamps are set according to the duration between beats.
        """
        self.tempo, self.timestamps = lr.beat.beat_track(self.amplitude_data, units='time')
        self.sleep_times = np.diff(self.timestamps)
        self.sleep_times = np.insert(self.sleep_times, 0, self.timestamps[0])
        self.num_chunks = len(self.sleep_times)  # break the song into chunks of time between each beat

    def compute_lightshow_data(self):
        """
        loop through the amplitude_data and determine the volume and contributing frequencies of each time chunk =-=-
        https://makersportal.com/blog/2018/9/13/audio-processing-in-python-part-i-sampling-and-the-fast-fourier-transform
        """
        self.lightshow_data = [['00000000'] * (len(self.freq_bins) - 1) for i in range(self.num_chunks)]
        data_array = [[0] * (len(self.freq_bins) - 1) for i in range(self.num_chunks)]
        self.volumes = np.zeros((self.num_chunks,))  # pre-define volume array
        average_freq_vals = np.zeros((len(self.freq_bins) - 1,))  # pre-define freq val array
        max_amp = max(self.amplitude_data)
        for chunk in range(0, self.num_chunks-1):  # loop through song in time chunks
            print('calculating {} / {} chunks'.format(chunk, self.num_chunks))
            n1 = round(self.sample_rate * self.timestamps[chunk])
            n2 = round(self.sample_rate * self.timestamps[chunk + 1])
            y_k = np.fft.fft(self.amplitude_data[int(n1):int(n2)])  # FFT function
            y_k = y_k[range(int((n2 - n1) / 2))]  # exclude sampling frequency
            y_k_power = np.abs(y_k)
            self.volumes[chunk] = max(self.amplitude_data[int(round(self.sample_rate * self.timestamps[chunk])):
                                                     int(round(self.sample_rate * self.timestamps[chunk + 1]))] / max_amp)

            for i in range(len(self.freq_bins) - 1):  # loop through freq bins and assign average FFT values to each one
                average_freq_vals[i] = statistics.mean(
                    y_k_power[int(self.freq_bins[i] * (self.timestamps[chunk + 1] - self.timestamps[chunk])):
                              int(self.freq_bins[i + 1] * (self.timestamps[chunk + 1] - self.timestamps[chunk]))])
            average_freq_vals /= max(average_freq_vals)  # normalize frequency values to max bin value for each chunk
            data_array[chunk] = average_freq_vals * self.volumes[chunk]
            i = 0
            for element in data_array[:][chunk]:
                if element < 0.05:
                    self.lightshow_data[chunk][i] = '00000000'
                elif 0.05 <= element < 0.125:
                    self.lightshow_data[chunk][i] = '10000000'
                elif 0.125 <= element < 0.25:
                    self.lightshow_data[chunk][i] = '11000000'
                elif 0.25 <= element < 0.375:
                    self.lightshow_data[chunk][i] = '11100000'
                elif 0.375 <= element < 0.5:
                    self.lightshow_data[chunk][i] = '11110000'
                elif 0.5 <= element < 0.625:
                    self.lightshow_data[chunk][i] = '11111000'
                elif 0.625 <= element < 0.75:
                    self.lightshow_data[chunk][i] = '11111100'
                elif 0.75 <= element < 0.875:
                    self.lightshow_data[chunk][i] = '11111110'
                elif element >= 0.875:
                    self.lightshow_data[chunk][i] = '11111111'
                i += 1

    def check_extension(self):
        if self.file.title().lower().endswith('.wav'):
            return True
        elif self.file.title().lower().endswith('.mp3'):
            print('C:/Users/John Grousopoulos/Documents/melody-lamp/songs/{}.mp3'.format(self.title))
            print('C:/Users/John Grousopoulos/Documents/melody-lamp/songs/{}.wav'.format(self.title))
            sound = AudioSegment.from_mp3('C:/Users/John Grousopoulos/Documents/melody-lamp/songs/{}.mp3'.format(self.title))
            sound.export('C:/Users/John Grousopoulos/Documents/melody-lamp/songs/{}.wav'.format(self.title), format="wav")
        else:
            print('Issue with the {} file extension, neither .mp3 nor .wav'.format(self.title))

    def plot_song_data(self):
        # create freq# data arrays before running this
        fig, (ax1, ax2) = plt.subplots(2, 1)
        import pdb
        pdb.set_trace()
        ax1.plot(self.amplitude_data)
        ax2.plot(self.timestamps, self.freq1_data, label='F1')
        ax2.plot(self.timestamps, self.freq2_data, label='F2')
        ax2.plot(self.timestamps, self.freq3_data, label='F3')
        ax2.plot(self.timestamps, self.freq4_data, label='F4')
        ax2.set_yscale('log')
        ax2.legend()

        # when plotting the FFT values for each time chunk in the song use this approach...
        # frequency_vec = self.sample_rate * np.arange((n / 2)) / n  # frequency vector
        # plt.plot(frequency_vec[0:len(y_k_power)], y_k_power)

        plt.show()

if __name__ == '__main__':
    directory = os.getcwd()
    playlist = glob(directory + '\songs\*.*')
    pickles = glob(directory + '\song_pickles\*.pkl')
    for audio_file in playlist:
        song_title = audio_file.title().split('\\')[-1].split('.')[0]
        print(song_title)
        print(pickles)
        import pdb
        pdb.set_trace()
        if song_title not in pickles: # change this to search pickles element-by-element
            current_song = Song(audio_file, song_title)  # create a song object which generates a pickle for the song
