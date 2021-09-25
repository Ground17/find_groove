import spectrogram
import os
import compare
from scipy.io import wavfile
import matplotlib.pyplot as plt

def find_weight(file1,file2):   
    '''
    두 음원의 매칭률을 최대화하는 spectrogram weight를 찾을 때 사용
    file1 : 원곡
    file2 : 녹음된 음원

    result : 매칭률을 최대화하는 weight
    '''
    match = 0
    for i in range(1,11):
        for j in range(1,11):
            ori_peaks = spectrogram.spectrogram(file1, i/10)     
            ori_finger = compare.rec_fingerprints(ori_peaks)
            rec_peaks = spectrogram.spectrogram(file2, j/10)     
            rec_finger = compare.rec_fingerprints(rec_peaks)
            offset = compare.compare(ori_finger, rec_finger)
            match_rate = offset/len(rec_finger)
            if match_rate > match:
                match = match_rate
                result = (i,j,match_rate)
            print(i,j, match_rate)
    print(result)
# spectrogram.spectrogram(file1)

def draw_sprgram(file1,file2, weight1, weight2):
    '''
    file1: 원곡
    file2: 녹음된 음원
    weight1: 원곡 스펙트로그램 가중치(0.6 추천)
    weight2: 녹음된 음원 스펙트로그램 가중치(1 추천)
    return: 스펙트로그램
    '''    
    plt.figure(figsize = (12,7))
    plt.subplot(2,1,1)
    plt.title('file1 Origin')
    spectrogram.spectrogram(file1, weight1)
    plt.subplot(2,1,2)
    plt.title('file2 Recorded')
    spectrogram.spectrogram(file2, weight2)
    plt.show()

# sample_fre, sigData = wavfile.read(file1)
# plt.specgram(sigData, Fs = sample_fre)
# plt.show()

def drawfft(file1, file2):
    '''
    file1: 원곡
    file2: 녹음된 음원
    return: 각각의 FFT 주파수 그래프
    '''
    audio1 = spectrogram.audioread(file1)
    audio2 = spectrogram.audioread(file2)
    fre1 = spectrogram.FFT(audio1)
    fre2 = spectrogram.FFT(audio2)
    N1 = len(audio1)
    N2 = len(audio2)
    f1 = [i/N1/2*11025 for i in range(int(N1/2))]
    f2 = [i/N2/2*11025 for i in range(int(N2/2))]
    plt.figure(1)
    plt.title('file1 Origin')
    plt.plot(f1,fre1)
    plt.figure(2)
    plt.title('file2 Recoreded')
    plt.plot(f2,fre2)
    plt.show()

def match_test(file):
    '''
    file: 녹음된(비교할) 음원
    return: 매칭 결과
    '''
    test_lists = compare.load_tuple()

    rec_peaks = spectrogram.spectrogram(file)     #녹음/일부 음원 스펙트로그램 적용
    rec_finger = compare.rec_fingerprints(rec_peaks)    #녹음된 음원 지문을 기록
    index = -1
    max_value = 0
    for i, v in enumerate(test_lists):
        file_name, test_list = v
        offset = compare.compare(test_list, rec_finger)  #비교 음원의 offset 차이의 최빈값을 구함
        if offset > 0:
            print(file_name, offset)
        if max_value < offset:
            max_value = offset
            index = i

    match_prob = max_value / len(rec_finger)
    if match_prob > 0.05:
        print("count:", max_value)
        print("result:", test_lists[index][0].replace('.txt','.wav'))
        print("probability:", match_prob * 100,"%")

if __name__ == "__main__":
    file2 = '../rec_music1.wav'
    file1 = '../data/genres/blues/blues.00001.wav'

    find_weight(file1,file2)
    # drawfft(file1,file2)
    # draw_sprgram(file1,file2, 0.6,1)
    # match_test(file1)
