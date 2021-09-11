"""
Song information to be saved and loaded from pickle files.
"""

import os
import pickle, json
import statistics
from glob import glob
import librosa as lr
import matplotlib.pyplot as plt
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
                 freq_bins=[0, 110, 410, 700, 20000]):

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
        self.low_low_data = []
        self.low_data = []
        self.high_data = []
        self.high_high_data = []
        self.amplitude_data = None
        self.json_data = {}

        self.check_extension()
        self.generate_data()
        self.generate_txt()
        # self.generate_json()
        # self.generate_pickle()
        
    def generate_data(self):
        """create a json file with the lightshow data."""
        self.compute_amplitude()
        self.beat_tracking()
        self.compute_lightshow_data()

        self.json_data = {'name':'','times':[],'low_low':[],'low':[],'high':[],'high_high':[]}
        self.json_data['name'] = self.title
        self.json_data['times'] = self.sleep_times
        self.json_data['low_low'] = self.low_low_data
        self.json_data['low'] = self.low_data
        self.json_data['high'] = self.high_data
        self.json_data['high_high'] = self.high_high_data
        # disp_song_data = input('plot song data? [Y/N]:   ')
        # if 'Y' in disp_song_data or 'y' in disp_song_data:
        #     self.plot_song_data()
    
    def generate_txt(self):
        with open('./song_data_txt/{}.txt'.format(self.title), 'w') as output:
            output.write(json.dumps(self.json_data))

    def generate_pickle(self):
        with open('./song_pickles/{}.json'.format(self.title), 'wb') as output:
            pickle.dump(self, output, protocol=4)
    
    def generate_json(self):
        with open('{}.json'.format(self.title), 'w') as output:
            json.dump(self.json_data, output)

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
        self.sleep_times = list(self.sleep_times)
        self.sleep_times = [i * 1000 for i in self.sleep_times]  # convert from [s] to [ms]
        self.sleep_times = [int(i) for i in self.sleep_times] # remove decimals
        self.num_chunks = len(self.sleep_times)  # break the song into chunks of time between each beat
        self.low_low_data = ['00000000']*self.num_chunks
        self.low_data = ['00000000']*self.num_chunks
        self.high_data = ['00000000']*self.num_chunks
        self.high_high_data = ['00000000']*self.num_chunks

    def compute_lightshow_data(self):
        """
        loop through the amplitude_data and determine the volume and contributing frequencies of each time chunk =-=-
        https://makersportal.com/blog/2018/9/13/audio-processing-in-python-part-i-sampling-and-the-fast-fourier-transform
        """
        # self.lightshow_data = [['00000000'] * (len(self.freq_bins) - 1) for i in range(self.num_chunks)]
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
                    # self.lightshow_data[chunk][i] = '00000000'
                    if i == 0: self.low_low_data[chunk] = '00000000' # 1 = 0
                    elif i == 1: self.low_data[chunk] = '00000000' # i = 1
                    elif i == 2: self.high_data[chunk] = '00000000' # i = 2
                    elif i == 3: self.high_high_data[chunk] = '00000000' # i = 3
                elif 0.05 <= element < 0.125:
                    # self.lightshow_data[chunk][i] = '10000000'
                    if i == 0: self.low_low_data[chunk] = '10000000' # 1 = 0
                    if i == 1: self.low_data[chunk] = '10000000' # i = 1
                    if i == 2: self.high_data[chunk] = '10000000' # i = 2
                    if i == 3: self.high_high_data[chunk] = '10000000' # i = 3
                elif 0.125 <= element < 0.25:
                    # self.lightshow_data[chunk][i] = '11000000'
                    if i == 0: self.low_low_data[chunk] = '11000000' # 1 = 0
                    if i == 1: self.low_data[chunk] = '11000000' # i = 1
                    if i == 2: self.high_data[chunk] = '11000000' # i = 2
                    if i == 3: self.high_high_data[chunk] = '11000000' # i = 3
                elif 0.25 <= element < 0.375:
                    # self.lightshow_data[chunk][i] = '11100000'
                    if i == 0: self.low_low_data[chunk] = '11100000' # 1 = 0
                    if i == 1: self.low_data[chunk] = '11100000' # i = 1
                    if i == 2: self.high_data[chunk] = '11100000' # i = 2
                    if i == 3: self.high_high_data[chunk] = '11100000' # i = 3
                elif 0.375 <= element < 0.5:
                    # self.lightshow_data[chunk][i] = '11110000'
                    if i == 0: self.low_low_data[chunk] = '11110000' # 1 = 0
                    if i == 1: self.low_data[chunk] = '11110000' # i = 1
                    if i == 2: self.high_data[chunk] = '11110000' # i = 2
                    if i == 3: self.high_high_data[chunk] = '11110000' # i = 3
                elif 0.5 <= element < 0.625:
                    # self.lightshow_data[chunk][i] = '11111000'
                    if i == 0: self.low_low_data[chunk] = '11111000' # 1 = 0
                    if i == 1: self.low_data[chunk] = '11111000' # i = 1
                    if i == 2: self.high_data[chunk] = '11111000' # i = 2
                    if i == 3: self.high_high_data[chunk] = '11111000' # i = 3
                elif 0.625 <= element < 0.75:
                    # self.lightshow_data[chunk][i] = '11111100'
                    if i == 0: self.low_low_data[chunk] = '11111100' # 1 = 0
                    if i == 1: self.low_data[chunk] = '11111100' # i = 1
                    if i == 2: self.high_data[chunk] = '11111100' # i = 2
                    if i == 3: self.high_high_data[chunk] = '11111100' # i = 3
                elif 0.75 <= element < 0.875:
                    # self.lightshow_data[chunk][i] = '11111110'
                    if i == 0: self.low_low_data[chunk] = '11111110' # 1 = 0
                    if i == 1: self.low_data[chunk] = '11111110' # i = 1
                    if i == 2: self.high_data[chunk] = '11111110' # i = 2
                    if i == 3: self.high_high_data[chunk] = '11111110' # i = 3
                elif element >= 0.875:
                    # self.lightshow_data[chunk][i] = '11111111'
                    if i == 0: self.low_low_data[chunk] = '11111111' # 1 = 0
                    if i == 1: self.low_data[chunk] = '11111111' # i = 1
                    if i == 2: self.high_data[chunk] = '11111111' # i = 2
                    if i == 3: self.high_high_data[chunk] = '11111111' # i = 3
                i += 1

    def check_extension(self):
        if self.file.title().lower().endswith('.wav'):
            return True
        # elif self.file.title().lower().endswith('.mp3'):
        #     print('C:/Users/John Grousopoulos/Documents/melody-lamp/songs/{}.mp3'.format(self.title))
        #     print('C:/Users/John Grousopoulos/Documents/melody-lamp/songs/{}.wav'.format(self.title))
        #     sound = AudioSegment.from_mp3('C:/Users/John Grousopoulos/Documents/melody-lamp/songs/{}.mp3'.format(self.title))
        #     sound.export('C:/Users/John Grousopoulos/Documents/melody-lamp/songs/{}.wav'.format(self.title), format="wav")
        else:
            print('Issue with the {} file extension, not .wav'.format(self.title))

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
    playlist = glob(directory + '\songs\*.wav')
    # pickles = glob(directory + '\song_pickles\*.pkl')
    for audio_file in playlist:
        song_title = audio_file.title().split('\\')[-1].split('.')[0]
        current_song = Song(audio_file, song_title)  # create a song object which generates a pickle for the song
