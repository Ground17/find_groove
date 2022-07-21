import numpy as np
import wave
import os
# import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter
import compare

def get_2D_peaks(frequencies, weight):
    '''
    :param frequencies:   audio frequency list
    :return:              array of over mean of band frequency

    각 주파수 밴드에서 가장 큰 주파수 값을 각각 얻어옵니다.
    '''
    f_10 = []
    f_20 = []
    f_40 = []
    f_80 = []
    f_160 = []
    f_320 = []
    f_511 = []

    for i in range(len(frequencies)):
        f_10.append(max(frequencies[i][0:15]))       #max frequency <= 107Hz very low
        f_20.append(max(frequencies[i][15:20]))      #107Hz < max frequency <= 214Hz low
        f_40.append(max(frequencies[i][20:40]))      # 214Hz < max frequency <= 428Hz low-mid
        f_80.append(max(frequencies[i][40:80]))      # 428Hz < max frequency <= 856Hz mid
        f_160.append(max(frequencies[i][80:160]))    # 856Hz < max frequency <= 1712Hz mid-high
        f_320.append(max(frequencies[i][160:320]))   # 1712Hz < max frequency <= 3445Hz high
        f_511.append(max(frequencies[i][320:511]))   # 3445Hz < max frequency <= 5491Hz very high

    mean_band = (max(f_40) + max(f_80) + max(f_160) + max(f_320) + max(f_511)) / 5 * weight  # 모든 시간에서 각 밴드의 최대값의 평균
    result = []
    for i in range(len(frequencies)):
        if f_10[i] > mean_band:
            result.append((frequencies[i][0:10].index(f_10[i]), i * 1024))
        if f_20[i] > mean_band:
            result.append((frequencies[i][18:20].index(f_20[i]) + 15, i * 1024))
        if f_40[i] > mean_band:
            result.append((frequencies[i][20:40].index(f_40[i]) + 20, i * 1024))        # 최대값의 주파수 인덱스와 시간 기록
        if f_80[i] > mean_band:
            result.append((frequencies[i][40:80].index(f_80[i]) + 40, i * 1024))
        if f_160[i] > mean_band:
            result.append((frequencies[i][80:160].index(f_160[i]) + 80, i * 1024))
        if f_320[i] > mean_band:
            result.append((frequencies[i][160:320].index(f_320[i]) + 160, i * 1024))
        if f_511[i] > mean_band:
            result.append((frequencies[i][320:511].index(f_511[i]) + 320, i * 1024))

    return result

def downsampling(files, sample=44100):
    '''

    :param file:    audio file
    :sample:        sample rate
    :return:        downsampled file, sampling rates = 4:1

    어떤 주파수의 소리이든, 11025Hz로 통일
    '''
    N = len(files)
    skip = sample // 11025
    down_file=[]
    
    # lowpass_filter 5kHz cutoff (aliasing 제거)
    nyq = 0.5 * sample
    normal_cutoff = 5000 / nyq
    order = 5
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    files = lfilter(b, a, files)

    for i in range(0, N, skip):
        if N - i < skip:
            temp = files[i:]
        else:
            temp = files[i:i + skip]
        down_file.append(sum(temp)/len(temp)) #시간을 평균내서 한 뭉텅이로 만듦

    return down_file

def FFT(audio_normalised):
    '''

    :param audio_normalised:    audio value in time domain
    :return:                    FFT of audio value

    들어온 오디오 정보의 FFT를 계산합니다.
    '''
    N = len(audio_normalised)
    frequency = np.fft.fft(audio_normalised) / N
    # frequency = frequency[range(math.trunc(N / 2))]
    frequency = frequency[range(int(N / 2))]
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

    웨이브 형식의 음악파일을 불러옵니다.
    '''

    # from pydub import AudioSegment

    # audio = AudioSegment.from_mp3(file)     #ffmpeg 다운로드 후 PATH 설정해야함

    # audio = np.array(audio.set_channels(1).get_array_of_samples())  #mp3 스테레오 중 1개의 채널만 가져와 배열로 변경
    # #max_int = 2**15                 #최대값
    # max_int = np.max(audio)
    # normal_audio = audio / max_int  #normalize 과정

    # return downsampling(normal_audio)
    ifile = wave.open(file)
    samples = ifile.getnframes()
    audio = ifile.readframes(samples)
    channel = ifile.getnchannels()

    audio_as_np_int16 = np.frombuffer(audio, dtype=np.int16)
    audio_as_np_float32 = audio_as_np_int16.astype(np.float32)

    if channel != 1:
        print(audio_as_np_float32.shape)
        audio_as_np_float32 = audio_as_np_float32.reshape((-1, 2))
        audio_as_np_float32 = audio_as_np_float32.sum(axis=1) / 2
        
        print(audio_as_np_float32.shape)

    max_int16 = 2 ** 15
    audio_normalised = audio_as_np_float32 / max_int16
    return downsampling(audio_normalised, ifile.getframerate())

def spectrogram(file, weight = 1):
    '''

    :param file:    wave file
    :return:        peaks of frequency and time in 2D

    get audio file -> normalise -> cut interval by using hammaing window
    -> FFT for all intervals -> get average magnitude of low frequency in a full song
    -> get peaks frequency over average magnitude

    이 코드 전체에서 가장 큰 뼈대입니다.
    오디오파일을 불러옵니다. -> 음악파일을 정규화 합니다 -> 해밍윈도우로 자릅니다.(크기 1024)
    -> 잘린 구간을 FFT합니다. -> 노래 전체 구간에서 저주파수 영역의 평균을 구합니다.
    -> 이 평균값보다 큰 주파수 영역대를 구합니다.
    '''

    audio_normalised = audioread(file) if isinstance(file, str) else file

    # summary = 0

    # for item in audio_normalised:
    #     summary += abs(item)
    # average = summary / len(audio_normalised)
    # if average < 0.1:
    #     for i in range(len(audio_normalised)):
    #         audio_normalised[i] *= 0.1 / average

    # print("average:", summary / len(audio_normalised))

    length = len(audio_normalised)
    window = np.hamming(1024) # 탭 수 1024인 해밍윈도우 생성

    frequencies = []
    # max_value = []
    # max_index = []

    for i in range(0, length - 1024, 1024):
        audio_cut = []
        for j in range(1024):
            audio_cut.append(window[j] * audio_normalised[i+j]) # 해밍윈도우로 자르기   
        frequency = FFT(audio_cut) # 잘린 부분 FFT 변환
        frequencies.append(frequency)

    peaks = get_2D_peaks(frequencies, weight)

    return peaks
