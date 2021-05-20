"""
Song information to be saved and loaded from pickle files.
"""

import pickle
import statistics

import librosa as lr
# import matplotlib.pyplot as plt
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
                 channels=2,
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
        self.channels = channels
        self.tempo = tempo  # song tempo in [bpm]
        self.num_chunks = num_chunks  # how many chunks the song is broken into for frequency analysis
        self.freq_bins = freq_bins  # upper cutoffs of frequency bins [Hz]
        self.lightshow_data = lightshow_data  # numpy 2d array of binary data x number of freq bins

        Song.generate_pickle(self)

    def generate_pickle(self):
        """
        open a pickle of the song data or create one if it doesn't exist.
        """
        amplitude_data = Song.compute_amplitude(self)  # obtain time series data
        Song.beat_tracking(self, amplitude_data=amplitude_data)  # determine beat locations
        Song.compute_lightshow_data(self, amplitude_data=amplitude_data)  # determine binary lists for shift registers

        with open('./song_pickles/{}.pkl'.format(self.title), 'wb') as output:
            pickle.dump(self, output, protocol=4)

    def compute_amplitude(self):
        amplitude_data, self.sample_rate = lr.load(self.file)  # time series amplitude data and sample frequency
        self.length = len(amplitude_data) / self.sample_rate  # length of song in seconds

        return amplitude_data

    def beat_tracking(self, amplitude_data):
        """
        calculate the tempo for the song and use the float value to re-calculate the chunk size.
        Timestamps are set according to the duration between beats.
        """
        self.tempo, self.timestamps = lr.beat.beat_track(amplitude_data, units='time')
        self.sleep_times = np.diff(self.timestamps)
        self.sleep_times = np.insert(self.sleep_times, 0, self.timestamps[0])
        self.num_chunks = len(self.sleep_times)  # break the song into chunks of time between each beat

    def compute_lightshow_data(self, amplitude_data):
        """
        loop through the amplitude_data and determine the volume and contributing frequencies of each time chunk =-=-
        https://makersportal.com/blog/2018/9/13/audio-processing-in-python-part-i-sampling-and-the-fast-fourier-transform
        """
        self.lightshow_data = [['00000000'] * (len(self.freq_bins) - 1) for i in range(self.num_chunks)]
        data_array = [[0] * (len(self.freq_bins) - 1) for i in range(self.num_chunks)]
        self.volumes = np.zeros((self.num_chunks,))  # pre-define volume array
        average_freq_vals = np.zeros((len(self.freq_bins) - 1,))  # pre-define freq val array
        max_amp = max(amplitude_data)
        for chunk in range(0, self.num_chunks-1):  # loop through song in time chunks
            print('calculating {} / {} chunks'.format(chunk, self.num_chunks))
            n1 = round(self.sample_rate * self.timestamps[chunk])
            n2 = round(self.sample_rate * self.timestamps[chunk + 1])
            y_k = np.fft.fft(amplitude_data[n1:n2])  # FFT function
            y_k = y_k[range(int((n2 - n1) / 2))]  # exclude sampling frequency
            y_k_power = np.abs(y_k)
            self.volumes[chunk] = max(amplitude_data[round(self.sample_rate * self.timestamps[chunk]):
                                                     round(self.sample_rate * self.timestamps[chunk + 1])] / max_amp)

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

    # def plot_song_data(self):
    #     pass
    # fig, (ax1, ax2) = plt.subplots(2, 1)
    # ax1.plot(self.amplitude_data)
    # ax2.plot(self.timestamps, self.lightshow_data['F1'], label='F1')
    # ax2.plot(self.timestamps, self.lightshow_data['F2'], label='F2')
    # ax2.plot(self.timestamps, self.lightshow_data['F3'], label='F3')
    # ax2.plot(self.timestamps, self.lightshow_data['F4'], label='F4')
    # ax2.set_yscale('log')
    # ax2.legend()

    # when plotting the FFT values for each time chunk in the song use this approach...
    # frequency_vec = self.sample_rate * np.arange((n / 2)) / n  # frequency vector
    # plt.plot(frequency_vec[0:len(y_k_power)], y_k_power)

    # plt.show()
