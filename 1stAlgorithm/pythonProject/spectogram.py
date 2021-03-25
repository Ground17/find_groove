import numpy as np
import wave
import math
import pandas as pd
import os

global fs
fs = 44100/4

def get_2D_peaks(array,array_index,avg,time):
    '''

    :param array:       frequency magnitude array
    :param array_index: frequency magnitude index array
    :param avg:         frequency average under 512Hz of a full length of song
    :param time:        time information of frequency
    :return:            list of tuple (frequency >= avg*weight , time)

    '''
    Nonzero_index=[]

    for i in range(len(array)):
        if array[i] >= avg:
            Nonzero_index.append((array_index[i]*fs/1024,time[i]))
    return Nonzero_index

def Low_fre(frequency):
    '''

    :param frequency:   frequency interval, size = 1024
    :return:            max value of low frequency(under 512Hz)


    '''
    f_10 = frequency[1]             #max frequency <= 10Hz
    f_20 = frequency[2]             #10Hz < max frequency <= 20Hz
    f_40 = max(frequency[3:5])      #20Hz < max frequency <= 40Hz
    f_80 = max(frequency[5:9])      #40Hz < max frequency <= 80Hz
    f_160 = max(frequency[9:16])    #80Hz < max frequency <= 160Hz
    f_511 = max(frequency[16:48])   #160Hz < max frequency <= 511Hz

    #return (f_10+f_20+f_40+f_80+f_160+f_511)/6
    return max([f_10,f_20,f_40,f_80,f_160,f_511])

def downsampling(file):
    '''

    :param file:    audio file
    :return:        downsampled file, sampling rates = 4:1

    '''
    N = len(file)
    down_file=[]

    for i in range(0,N,4):
        sum = 0
        for j in range(4):
            sum += file[i+j]
        down_file.append(sum/4)

    return down_file

def FFT(audio_normalised):
    '''

    :param audio_normalised:    audio value in time domain
    :return:                    FFT of audio value
    '''
    N = len(audio_normalised)
    frequency = np.fft.fft(audio_normalised) / N
    frequency = frequency[range(math.trunc(N / 2))]
    frequency = 2 * abs(frequency)
    frequency = frequency.tolist()
    #f0 = np.arange(N) / N
    #f0 = f0[range(math.trunc(N / 2))] * fs

    #max_magnitude = max(frequency)
    #max_index = frequency.index(max_magnitude)
    #print(max_index)
    return frequency

def audioread(file):
    '''

    :param file:    audio file.wav
    :return:        downsampled wave file
    '''
    ifile = wave.open(file)
    samples = ifile.getnframes()
    audio = ifile.readframes(samples)

    audio_as_np_int16 = np.frombuffer(audio, dtype=np.int16)
    audio_as_np_float32 = audio_as_np_int16.astype(np.float32)

    max_int16 = 2 ** 15
    audio_normalised = audio_as_np_float32 / max_int16
    return downsampling(audio_normalised)

def spectogram(file):
    '''

    :param file:    wave file
    :return:        peaks of frequency and time in 2D

    get audio file -> normalise -> cut interval by using hammaing window
    -> FFT for all intervals -> get average magnitude of low frequency in a full song
    -> get peaks frequency over average magnitude

    '''
    global fs

    audio_normalised = audioread(file)

    length = len(audio_normalised)
    window = np.hamming(1024)

    low_frequency = []
    max_value = []
    max_index = []
    for i in range(0,length-1024,1024):
        audio_cut = []
        for j in range(1024):
            audio_cut.append(window[j]*audio_normalised[i+j])
        frequency = (FFT(audio_cut))
        low_frequency.append(Low_fre(frequency))
        max_frequency = max(frequency)
        max_value.append(max_frequency)
        max_index.append(frequency.index(max_frequency))

    Low_avg = sum(low_frequency)/len(low_frequency)
    #time = np.arange(0,length - 1024, 1024)
    time = np.arange(0, length - 1024, 1024) / fs / 2

    peaks = get_2D_peaks(max_value, max_index, Low_avg*1.2, time)
    #fre_time = final_frequency*fs/1024

    '''fre = []
    time = []
    for i in range(len(peaks)):
        fre.append(peaks[i][0])
        time.append(peaks[i][1])

    plt.plot(time,fre,'x',alpha = 0.2)
    plt.show()'''

    return peaks

path = './musics/'
music_list = os.listdir(path)
#music_list = glob.glob(path)

fan_value = 15
for k in music_list:
    peaks = spectogram('./musics/'+k)

    data = []
    for i in range(len(peaks)):
        for j in range(1, fan_value):
            if (i+j) < len(peaks):

                freq1 = peaks[i][0]
                freq2 = peaks[i + j][0]
                t1 = peaks[i][1]
                t2 = peaks[i + j][1]
                t_delta = t2 - t1

                if t_delta <= 200:
                    data.append((freq1,freq2,t_delta))


    df = pd.DataFrame(data)

    df.to_csv('C:/Users/moonm/PycharmProjects/pythonProject/fingerprints/'+k)

