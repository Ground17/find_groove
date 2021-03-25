import spectogram
import os

#Uncompleted!!!

def text2tuple(file):

    test_list = []

    while True:
        line = file.readline()
        if not line: break
        line = line.strip()
        tmp_line = line.split(',')
        test_list.append([(int(tmp_line[0]), int(tmp_line[1]), int(tmp_line[2])), int(tmp_line[3])])
    return test_list

def rec_fingerprints(rec_peaks):
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

file = open(path_data+data[0],'r')
test_list = text2tuple(file)

rec_peaks = spectogram.spectogram('C:/Users/moonm/PycharmProjects/pythonProject/records/'+rec[0])
rec_finger = rec_fingerprints(rec_peaks)

count = 0
result = []
for rec_tuple, rec_offset in rec_finger:
    for tuple, offset in test_list:
        if rec_tuple not in tuple:
           count = 0
        else :
            count += 1

print(rec_finger)



