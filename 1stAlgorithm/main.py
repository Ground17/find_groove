import spectogram
import os

def matching(offset_list):
    '''
    Match music

    :param offset_list: get offsets tuple(the music name, offset )
    :return:            find the matched music

    음악을 찾는 함수
    offset_list : 튜플(음원 이름, 오프셋 차이의 최빈값)

    '''
    max = 0
    index = 0
    for i in range(len(offset_list)):   #offset_list의 길이 = 음원의 총 개수
        if max < offset_list[i][1]:     #offset 차이의 최빈값이 가장 큰 음원을 찾는다
            max = offset_list[i][1]
            index = i                   #음원의 이름이 위치한 인덱스

    return offset_list[index][0]        #찾은 음원의 이름 반환

def mode(arr):
    '''

    :param arr:     any list or array
    :return:        find the most appearing value in list

    오프셋 리스트에서 가장 많이 나오는 값을 찾습니다.(최빈값 찾기)
    '''

    max_count = 0
    counter = set(arr)
    for c in counter:
        if max_count < arr.count(c):
            max_count = arr.count(c)

    return max_count

def compare(test_list, rec_finger):

    '''
    Calculation of the difference of offsets

    :param test_list:       The original music data
    :param rec_finger:      The recorded music data
    :return:                The list of the offsets between the origin and recorded

    원곡과 녹음된 곡의 지문 정보(freq1, freq2, t_delta)가 일치할 때마다 오프셋 차이를 계산하여 추가합니다.
    이 오프셋 차이값들이 많이 기록될수록, 해당 음원이 맞을 확률이 높아집니다.
    '''
    result = []
    for tuple, offset in test_list:                 #음원과 녹음된 음원의 데이터를 일일이 비교
        for rec_tuple, rec_offset in rec_finger:    
            if rec_tuple == tuple:                  #데이터가 일치할 때마다
                result.append(offset - rec_offset)  #두 오프셋의 차이를 기록함
    return mode(result)


def text2tuple(file):
    '''
    Transform the file.txt to tuple

    :param file:        A file.txt
    :return:            List[[(tuple),offset]]

    텍스트 형식으로 기록된 지문 정보를 숫자계산이 가능하도록 정수 튜플로 바꿉니다.
    '''
    test_list = []

    while True:
        line = file.readline()
        if not line: break
        line = line.strip()
        tmp_line = line.split(',')
        test_list.append([(int(tmp_line[0]), int(tmp_line[1]), int(tmp_line[2])), int(tmp_line[3])])
    return test_list

def rec_fingerprints(rec_peaks):
    '''
    Get a fingerprint of recorded music

    :param rec_peaks:       A recorded music in spectogram
    :return:                List[[(tuple),offset]]

    녹음/일부 음원의 스펙트로그램으로 지문을 만듭니다
    시간이 t1일 때 주파수 값 freq1, 시간이 t2일 때 주파수 값 freq2를 얻습니다.
    t_delta는 구간 t1~t2 길이(인덱스 차이)
    여기서 t1은 구간의 시작점을 알려주는 offset의 역할을 합니다.

    data에 저장되는 정보 : (freq1,freq2,t_delta),t1

    '''
    fan_value = 15                                              #지문에서 탐색할 주파수 인덱스 범위
    data = []                                                   #지문 정보가 들어갈 리스트

    for i in range(len(rec_peaks)):                             #스펙트로그램 주파수 영역 길이만큼
        for j in range(1, fan_value):                           #설정한 인덱스 범위만큼
            if (i+j) < len(rec_peaks):                          #녹음된 음원의 길이를 넘지 않게

                freq1 = rec_peaks[i][0]
                freq2 = rec_peaks[i + j][0]
                t1 = rec_peaks[i][1]
                t2 = rec_peaks[i + j][1]
                t_delta = t2 - t1                               #시간 인덱스 차이

                if t_delta <= 1024*20:                          #인덱스 차이가 1024*20(약 1.85초) 이내일 경우만 기록
                    data.append([(freq1,freq2,t_delta),t1])
    return data

path_data = './fingerprints/'
path_rec = './records'
data = os.listdir(path_data)
rec = os.listdir(path_rec)

rec_peaks = spectogram.spectogram('C:/Users/moonm/PycharmProjects/pythonProject/records/' + rec[0])     #녹음/일부 음원 스펙트로그램 적용
rec_finger = rec_fingerprints(rec_peaks)    #녹음된 음원 지문을 기록

offset_list=[]
for file_name in data:
    file = open(path_data+file_name,'r')
    test_list = text2tuple(file)


    offset = compare(test_list, rec_finger)                         #비교 음원의 offset 차이의 최빈값을 구함
    offset_list.append((file_name.replace('.txt','.wav'),offset))   #음원 이름과 offset 차이의 최빈값을 추가함

print(matching(offset_list))





