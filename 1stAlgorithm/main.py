import spectogram
import os

def matching(offset_list):
    '''
    Match music

    :param offset_list: get offsets tuple(the music name, offset )
    :return:            find the matched music
    '''
    max = 0
    index = 0
    for i in range(len(offset_list)):
        if max < offset_list[i][1]:
            max = offset_list[i][1]
            index = i

    return offset_list[index][0]

def mode(arr):
    '''

    :param arr:     any list or array
    :return:        find the most appearing value in list
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
    '''
    result = []
    for tuple, offset in test_list:
        for rec_tuple, rec_offset in rec_finger:
            if rec_tuple == tuple:
                result.append(offset - rec_offset)
    return mode(result)


def text2tuple(file):
    '''
    Transform the file.txt to tuple

    :param file:        A file.txt
    :return:            List[[(tuple),offset]]
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
    '''
    fan_value = 15
    data = []

    for i in range(len(rec_peaks)):
        for j in range(1, fan_value):
            if (i+j) < len(rec_peaks):

                freq1 = rec_peaks[i][0]
                freq2 = rec_peaks[i + j][0]
                t1 = rec_peaks[i][1]
                t2 = rec_peaks[i + j][1]
                t_delta = t2 - t1

                if t_delta <= 1024*20:
                    data.append([(freq1,freq2,t_delta),t1])
    return data

path_data = './fingerprints/'
path_rec = './records'
data = os.listdir(path_data)
rec = os.listdir(path_rec)

rec_peaks = spectogram.spectogram('C:/Users/moonm/PycharmProjects/pythonProject/records/' + rec[0])
rec_finger = rec_fingerprints(rec_peaks)

offset_list=[]
for file_name in data:
    file = open(path_data+file_name,'r')
    test_list = text2tuple(file)


    offset = compare(test_list, rec_finger)
    offset_list.append((file_name.replace('.txt','.wav'),offset))

print(matching(offset_list))





