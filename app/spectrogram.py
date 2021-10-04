import numpy as np
import wave
import math
import os
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter
import compare

global fs
fs = 44100/4

# def get_2D_peaks(array,array_index,avg,time):
#     '''

#     :param array:       frequency magnitude array
#     :param array_index: frequency magnitude index array
#     :param avg:         frequency average under 512Hz of a full length of song
#     :param time:        time information of frequency
#     :return:            list of tuple (frequency >= avg*weight , time)

#     주파수 영역에서 평균값 * 보정값보다 큰 주파수와 그 때의 시간 정보를 얻어옵니다.
#     보정값은 설계자가 임의로 설정 가능
#     '''
#     Nonzero_index=[]                                        #평균값 * 보정값보다 큰 주파수 인덱스들의 모임

#     for i in range(len(array)):
#         if array[i] >= avg:
#             Nonzero_index.append((array_index[i],time[i]))  #[0]: 주파수 [1]: 시간
#     return Nonzero_index

def get_2D_peaks(frequencies, weight):
    '''

    :param frequencies:   audio frequency list
    :return:              array of over mean of band frequency

    각 주파수 밴드에서 가장 큰 주파수 값을 각가 얻어옵니다.
    '''
    # f_10 = []
    # f_20 = []
    f_40 = []
    f_80 = []
    f_160 = []
    f_320 = []
    f_511 = []

    for i in range(len(frequencies)):
    #     f_10.append(max(frequencies[i][0:15]))       #max frequency <= 107Hz very low
    #     f_20.append(max(frequencies[i][15:20]))      #107Hz < max frequency <= 214Hz low
        f_40.append(max(frequencies[i][18:40]))      #193Hz < max frequency <= 428Hz low-mid
        f_80.append(max(frequencies[i][40:80]))      #428Hz < max frequency <= 856Hz mid
        f_160.append(max(frequencies[i][80:160]))    #856Hz < max frequency <= 1712Hz mid-high
        f_320.append(max(frequencies[i][160:320]))   #1712Hz < max frequency <= 3445Hz high
        f_511.append(max(frequencies[i][320:511]))   #3445Hz < max frequency <= 5491Hz very high

    mean_band = (max(f_40)+max(f_80)+max(f_160)+max(f_320)+max(f_511))/5 * weight  #모든 시간에서 각 밴드의 최대값의 평균
    result = []
    for i in range(len(frequencies)):
        # if f_10[i] > mean_band:
        #     result.append((frequencies[i][0:10].index(f_10[i]), i * 1024))
        # if f_20[i] > mean_band:
        #     result.append((frequencies[i][18:20].index(f_20[i]) + 15, i * 1024))
        if f_40[i] > mean_band:
            result.append((frequencies[i][18:40].index(f_40[i]) + 18, i * 1024))        #최대값의 주파수 인덱스와 시간 기록
        if f_80[i] > mean_band:
            result.append((frequencies[i][40:80].index(f_80[i]) + 40, i * 1024))
        if f_160[i] > mean_band:
            result.append((frequencies[i][80:160].index(f_160[i]) + 80, i * 1024))
        if f_320[i] > mean_band:
            result.append((frequencies[i][160:320].index(f_320[i]) + 160, i * 1024))
        if f_511[i] > mean_band:
            result.append((frequencies[i][320:511].index(f_511[i]) + 320, i * 1024))

    return result
    #return max([f_10,f_20,f_40,f_80,f_160,f_511])

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
    이것은 큰 저장공간이 필요하므로 mp3로 바꿔야합니다.
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
    global fs

    audio_normalised = audioread(file) if isinstance(file, str) else file # 녹음파일의 경우 바로 쓸 수 있음

    # summary = 0

    # for item in audio_normalised:
    #     summary += abs(item)
    # average = summary / len(audio_normalised)
    # if average < 0.1:
    #     for i in range(len(audio_normalised)):
    #         audio_normalised[i] *= 0.1 / average

    # print("average:", summary / len(audio_normalised))

    length = len(audio_normalised)
    window = np.hamming(1024)                                   #탭 수 1024인 해밍윈도우 생성
    # window_512 = np.hamming(512)

    frequencies = []
    # max_value = []
    # max_index = []

    for i in range(0, length - 1024, 1024):
        audio_cut = []
        for j in range(1024):
            audio_cut.append(window[j]*audio_normalised[i+j])   #해밍윈도우로 자르기   
        frequency = FFT(audio_cut)                              #잘린 부분 FFT 변환
        frequencies.append(frequency)

    peaks = get_2D_peaks(frequencies, weight)
    # for i in range(len(frequencies)):
    #     # for j in range(512):
    #     #     frequencies[i][j] -= summary[j]
    #     # frequencies[i][0] = frequencies[i][1] = 0
    #     band_frequency.append(band_fre(frequencies[i]))                #6개 밴드 주파수 영역에서 가장 큰 주파수 크기 등록
    #     max_frequency = max(frequencies[i])                          #잘린 구간에서 모든 주파수 영역에서의 가장 큰 주파수 크기 가져오기
    #     max_value.append(max_frequency)                         #가장 큰 주파수 크기 등록
    #     max_index.append(frequencies[i].index(max_frequency))        #가장 큰 주파수 크기의 인덱스(주파수) 등록

    # Low_avg = sum(band_frequency)/len(band_frequency)             #모든 시간영역에서 가장 큰 밴드 주파수 크기의 평균값
    # time = np.arange(0, length - 1024, 1024)                     #시간 array
    #time = np.arange(0, length - 1024, 1024) / fs / 2

    # peaks = get_2D_peaks(max_value, max_index, 1.2, time)   #평균보다 큰 주파수 크기와 그 때의 주파수, 시간을 구함
    #fre_time = final_frequency*fs/1024

    #스펙트로그램 확인하고 싶을 때 활성화
    fre = []
    time = []
    for i, peak in enumerate(peaks):
        fre.append(peak[0])
        time.append(peak[1])

    plt.scatter(np.array(time)/fs,fre,marker = 'x',alpha = 0.2)
    # plt.show()

    return peaks

#music_list = glob.glob(path)
'''
    fingerprint를 얻는 과정입니다.
'''
if __name__ == "__main__": # 로컬 가상 서버에서만 호출합니다.
    # cwd = os.getcwd()
    # path = '../data/genres'
    path = '../data/rec_data'
    music_list = os.listdir(path)
    music_list = [item for item in music_list if os.path.isdir(os.path.join(path, item))] # 장르 10개 (['blues', 'classical', 'country', 'disco', 'hiphop', 'jazz', 'metal', 'pop', 'reggae', 'rock'])

    fan_value = 15                                            #특정 인덱스 기준 몇번째까지 범위를 가질것인가
    for k in music_list:
        genre_path = path + '/' + k
        for l in os.listdir(genre_path):
            peaks = spectrogram(genre_path + "/" + l, weight = 0.6)
            f = open('../data/rec_fingerprints/'+l.replace('.wav','.txt'), 'w')
            # f = open('../data/fingerprints/'+l.replace('.wav','.txt'), 'w')    #fingerprints 폴더에 파일 이름 생성
            for i in range(len(peaks)):
                for j in range(1, fan_value):
                    if (i+j) < len(peaks):                                  #인덱스가 범위 내에 있다면
                        freq1 = peaks[i][0]                                 #주파수1 인덱스
                        freq2 = peaks[i + j][0]                             #주파수2 인덱스
                        t1 = peaks[i][1]                                    #시간1 인덱스
                        t2 = peaks[i + j][1]                                #시간2 인덱스
                        t_delta = t2 - t1

                        if t_delta <= 1024*20:                              #특정 시간 이내라면
                            f.write(str(freq1)+','+str(freq2)+','+str(t_delta)+','+str(t1)+'\n') #주파수1, 주파수2, 시간차, 시간1 저장


            f.close()
            print(l)
    compare.save_tuple()
    '''df = pd.DataFrame(data)

    df.to_csv('C:/Users/moonm/PycharmProjects/pythonProject/fingerprints/'+k.replace('.wav','.csv'), index = False, header = False)
    '''

