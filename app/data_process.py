# ML, DL용 input 데이터 전처리 과정
import numpy as np
import matplotlib.pyplot as plt
import librosa, librosa.display
import tensorflow as tf
import wave
import math
import os
from scipy.signal import butter, lfilter

def downsampling(files, sample=44100):
    '''

    :param file:    audio file
    :sample: sample rate (무조건 44100의 약수여야 함)
    :return:        downsampled file, sampling rates = 4:1

    44100Hz는 데이터가 너무 커서 0.25배로 다운샘플링
    '''
    N = len(files)
    skip = sample // 11025
    down_file=[]
    
    # lowpass_filter 5kHz cutoff (aliasing 제거)
    if sample > 11025:
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
    frequency = frequency[range(math.trunc(N / 2))]
    frequency = 2 * abs(frequency)
    frequency = frequency.tolist()

    return frequency

def audioread(file):
    '''

    :param file:    audio file.wav
    :return:        downsampled wave file

    웨이브 형식의 음악파일을 불러옵니다.
    이것은 큰 저장공간이 필요하므로 mp3로 바꿔야합니다.
    '''
    ifile = wave.open(file)
    samples = ifile.getnframes()
    audio = ifile.readframes(samples)
    channel = ifile.getnchannels()

    audio_as_np_int16 = np.frombuffer(audio, dtype=np.int16)
    audio_as_np_float32 = audio_as_np_int16.astype(np.float32)

    if channel != 1:
        audio_as_np_float32 = audio_as_np_float32.reshape((-1, 2))
        audio_as_np_float32 = audio_as_np_float32.sum(axis=1) / 2

    max_int16 = 2 ** 15
    audio_normalised = audio_as_np_float32 / max_int16
    return downsampling(audio_normalised, ifile.getframerate())

def add_noise(noise, std, length):
    return np.random.normal(0, std * noise, size=length)

def spectrogram(file, noise=0, offset=0):
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
    audio_array = audioread(file) if isinstance(file, str) else file # 녹음파일의 경우 바로 쓸 수 있음
    audio_normalised = np.array(audio_array)
    std = np.std(audio_normalised)
    length = len(audio_normalised)

    if isinstance(file, str) and noise != 0:
        audio_normalised += add_noise(noise, std, length)

    
    window = np.hamming(1024)                                   #탭 수 1024인 해밍윈도우 생성

    frequencies = []

    for i in range(0, length - 1024, 1024):
        audio_cut = []
        for j in range(1024):
            audio_cut.append(window[j]*audio_normalised[i+j])   #해밍윈도우로 자르기   
        frequency = FFT(audio_cut)                              #잘린 부분 FFT 변환
        frequencies.append(frequency)

    return frequencies