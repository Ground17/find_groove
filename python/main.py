import spectogram
import os
import pickle
import time

# def matching(offset_list):
#     '''
#     Match music

#     :param offset_list: get offsets tuple(the music name, offset )
#     :return:            find the matched music

#     음악을 찾는 함수
#     offset_list : 튜플(음원 이름, 오프셋 차이의 최빈값)

#     '''
#     max_value = 0
#     index = 0
#     for i in range(len(offset_list)):   #offset_list의 길이 = 음원의 총 개수
#         print(offset_list[i][0], offset_list[i][1])
#         if max_value < offset_list[i][1]:     #offset 차이의 최빈값이 가장 큰 음원을 찾는다
#             max_value = offset_list[i][1]
#             index = i                   #음원의 이름이 위치한 인덱스

#     return offset_list[index][0]        #찾은 음원의 이름 반환

# def mode(arr):
#     '''

#     :param arr:     any list or array
#     :return:        find the most appearing value in list

#     오프셋 리스트에서 가장 많이 나오는 값을 찾습니다.(최빈값 찾기)
#     '''

#     max_count = 0
#     counter = set(arr)
#     for c in counter:
#         if max_count < arr.count(c):
#             max_count = arr.count(c)

#     return max_count

def compare(test_list, rec_finger):

    '''
    Calculation of the difference of offsets

    :param test_list:       The original music data
    :param rec_finger:      The recorded music data
    :return:                The list of the offsets between the origin and recorded

    원곡과 녹음된 곡의 지문 정보(freq1, freq2, t_delta)가 일치할 때마다 오프셋 차이를 계산하여 추가합니다.
    이 오프셋 차이값들이 많이 기록될수록, 해당 음원이 맞을 확률이 높아집니다.
    '''
    result = {}

    minimal = 10
    length = len(rec_finger)
    check = False

    for tuple_value, offset in test_list:   #음원과 녹음된 음원의 데이터를 일일이 비교
        if check:
            length -= 1
            if length < 0:
                check = False
                length = len(rec_finger)
        for i, value in enumerate(rec_finger):   
            rec_tuple, rec_offset = value
            if i >= minimal and not check:
                break

            if rec_tuple == tuple_value:    
                check = True              #데이터가 일치할 때마다
                length = len(rec_finger)
                if offset - rec_offset in result: #두 오프셋의 차이를 기록함
                    result[offset - rec_offset] += 1
                else:
                    result[offset - rec_offset] = 1

    return max(result.values()) if len(result) > 0 else 0


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
    f = open('./fingerprints/records.txt', 'w')
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
                    f.write(str(freq1)+','+str(freq2)+','+str(t_delta)+','+str(t1)+'\n') #주파수1, 주파수2, 시간차, 시간1 저장
    f.close()           
    return data

def save_tuple(): # fingerprint 튜플 저장 
    path_data = '../data/fingerprints/'
    data = os.listdir(path_data)
    test_lists = []

    for file_name in data:
        file = open(path_data + file_name,'r')
        test_lists.append((file_name, text2tuple(file)))

    with open('./variables/test_lists', 'wb') as f:
        pickle.dump(test_lists, f)

def load_tuple(): # fingerprint 튜플 불러오기
    with open('./variables/test_lists', 'rb') as f:
        return pickle.load(f)

if __name__ == "__main__":
    save_tuple() # 생략 가능
    start = time.time()
    test_lists = load_tuple()
    path_rec = './records/'
    rec = os.listdir(path_rec)

    rec_peaks = spectogram.spectogram(path_rec + rec[4])     #녹음/일부 음원 스펙트로그램 적용
    rec_finger = rec_fingerprints(rec_peaks)    #녹음된 음원 지문을 기록
    index = -1
    max_value = 0
    for i, v in enumerate(test_lists):
        file_name, test_list = v
        offset = compare(test_list, rec_finger)  #비교 음원의 offset 차이의 최빈값을 구함
        if offset > 0:
            print(file_name, offset)
        if max_value < offset:
            max_value = offset
            index = i
    if max_value > 0:
        print("count:", max_value)
        print("result:", test_lists[index][0].replace('.txt','.wav'))
        print("time:", time.time() - start)
    else:
        print("result: None")
        print("time: ", time.time() - start)
    





