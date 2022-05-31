import datetime
import time

from flask import Flask, render_template, request, jsonify
import compare
import spectrogram
import tensorflow as tf
import os
import numpy as np
import pickle
import tkinter
from tkinter import Button, Label
import tkinter.ttk
from tkinter.filedialog import askdirectory

window=tkinter.Tk()
window.title("Find Groove")

is_model = False

def draw_window_1():
    description1 = Label(window, text="1. Choose a folder(directory) that contains *.wav file(s).")
    directory_btn = Button(window, text='Select', command=directory)
    description1.grid(row=0, column=0, columnspan=2)
    directory_btn.grid(row=0, column=2)

def directory():
    global filepath
    filepath = askdirectory(title="Dialog box", initialdir=os.getcwd())
    label_path = Label(window, text=filepath)
    label_path.grid(row=1, column=0, columnspan=3)

    # show for making fingerprint
    if filepath:
        description2 = Label(window, text="2. Make a fingerprint file.\nIf 'fingerprints' is already in the path, skip this process.")
        fingerprint_btn = Button(window, text='Make', command=make_fingerprint)
        skip_btn = Button(window, text='Skip', command=load_tuple)
        description2.grid(row=2, column=0)
        skip_btn.grid(row=2, column=1)
        fingerprint_btn.grid(row=2, column=2)

def make_fingerprint():
    global filepath, finger_dict
    music_list = os.listdir(filepath)
    music_list = [item for item in music_list if os.path.isfile(os.path.join(filepath, item)) and item.split('.')[-1] == 'wav'] # pick *.wav files

    fan_value = 15 # 특정 인덱스 기준 몇번째까지 범위를 가질것인가
    finger_dict = {}
    progressbar=tkinter.ttk.Progressbar(window, maximum=len(music_list), mode="indeterminate")
    progressbar.grid(row=3, column=0, columnspan=3)
    progressbar.start(50)
    for name in music_list:
        print(name)
        peaks = spectrogram.spectrogram(filepath + "/" + name, weight = 0.6)
        for i in range(len(peaks)):
            for j in range(1, fan_value):
                if (i + j) < len(peaks): # 인덱스가 범위 내에 있다면
                    freq1 = peaks[i][0] # 주파수1 인덱스
                    freq2 = peaks[i + j][0] # 주파수2 인덱스
                    t1 = peaks[i][1] # 시간1 인덱스
                    t2 = peaks[i + j][1] # 시간2 인덱스
                    t_delta = t2 - t1

                    if t_delta <= 1024 * 20:
                        if (freq1, freq2, t_delta) not in finger_dict:
                            finger_dict[(freq1, freq2, t_delta)] = set()

                        finger_dict[(freq1, freq2, t_delta)].add((name, t1)) # key: (freq1, freq2, t_delta), value: (filename, t1)

        progressbar.step(1)
        progressbar.update()

    with open(filepath + '/fingerprints', 'wb') as f:
        pickle.dump(finger_dict, f)

    progressbar.stop()

    draw_window_3()

def load_tuple(): # load fingerprint 튜플 불러오기
    global filepath, finger_dict
    with open(filepath + '/fingerprints', 'rb') as f:
        finger_dict = pickle.load(f)
    
    draw_window_3()

def draw_window_3():
    description3 = Label(window, text="3. Verify that the tensorflow model is in the path.\nSee 'https://github.com/Ground17/find_groove' for a detailed description of the model.")
    directory_btn = Button(window, text='Check', command=check_model)
    description3.grid(row=4, column=0, columnspan=2)
    directory_btn.grid(row=4, column=2)

def check_model(): # tensorflow model을 사용할 것인지 체크
    global filepath, is_model, model
    if os.path.exists(filepath + '/cnn_vote_best_total.h5'):
        model = tf.keras.models.load_model(filepath + '/cnn_vote_best_total.h5')
        is_model = True
    else:
        is_model = False

    label_model = Label(window, text="We can use tensorflow model!" if is_model else "We can't use tensorflow model.")
    label_model.grid(row=5, column=0, columnspan=3)

    draw_window_4()

def draw_window_4():
    description4 = Label(window, text="4. Turn on the server. You can test searching music by '127.0.0.1:8000'.\n모바일에서 사용하려면 방화벽 등도 체크해야 함을 언급...")
    directory_btn = Button(window, text='Turn on', command=run_local)
    description4.grid(row=6, column=0, columnspan=2)
    directory_btn.grid(row=6, column=2)

def run_local(port=8080, public=True):
    global test_lists
    app.run(host='0.0.0.0' if public else '127.0.0.1', port=port, debug=True)

draw_window_1()
window.mainloop()
    
app = Flask(__name__)

@app.route('/', methods=['GET'])
def main():
    dummy_times = [datetime.datetime(2021, 10, 8, 23, 59, 59)]
    return render_template('index.html', times=dummy_times)

@app.route('/search', methods=['POST'])
def search():
    start = time.time()
    # f = request.files['file']
    # f.save('./files/' + secure_filename(f.filename))

    params = request.get_json()

    # samples: 11025Hz로 샘플링된 float 형식 4초 분량 녹음 데이터
    samples = params['samples']

    # 1. ml model
    genre = [
        "blues",
        "classical",
        "country",
        "disco",
        "hiphop",
        "jazz",
        "metal",
        "pop",
        "reggae",
        "rock",
        ]
    array_X = []
    ffts = params['data'] # (length, 512) => (512, 30)
    temp30 = []
    for m in range(len(ffts)): # 30개씩 쌓기
        for n in range(30):
            if m + n < len(ffts):
                temp30.append(ffts[m + n])      
        if len(temp30) == 30:
            array_X.append(temp30)
            temp30 = []

    train_X = np.array(array_X)

    for i in range(len(train_X)): # 데이터 정규화
        for j in range(len(train_X[i])):
            if np.std(train_X[i, j]) == 0:
                continue
            train_X[i, j] = (train_X[i, j] - np.mean(train_X[i, j])) / np.std(train_X[i, j])

    train_X = np.swapaxes(train_X, 1, 2)

    train_X = train_X[..., np.newaxis]
    count = [0 for _ in range(100)]

    answer = []
    for i, c in enumerate(count):
        answer.append((c, i))
    answer.sort(reverse=True)

    # 2. fingerprint
    rec_peaks = spectrogram.spectrogram(samples)     #녹음/일부 음원 스펙트로그램 적용
    rec_finger = compare.rec_fingerprints(rec_peaks)    #녹음된 음원 지문을 기록
    index = -1
    max_value = 0
    for i, v in enumerate(test_lists):
        file_name, test_list = v
        offset = compare.compare(test_list, rec_finger)  #비교 음원의 offset 차이의 최빈값을 구함
        # if offset > 0:
        #     print(file_name, offset)
        if max_value < offset:
            max_value = offset
            index = i

    # if max_value > 0:
    #     print("count:", max_value)
    #     print("result:", test_lists[index][0].replace('.txt','.wav'))
    #     print("time:", time.time() - start)
    # else:
    #     print("result: None")
    #     print("time: ", time.time() - start)

    match_prob = max_value / len(rec_finger)
    # if match_prob > 0.05:
    #     print("result:", test_lists[index][0].replace('.txt',''))
    #     print("probability:", match_prob * 100,"%")
    #     print("time:", time.time() - start)

    # fingerprint, model에서 나온 모든 정보 정리
    title = ""
    recommend1 = ""
    recommend2 = ""
    recommend3 = ""
    accuracy = 0.0

    if "%s.0000%d"%(genre[answer[0][1] // 10], answer[0][1] % 10) == test_lists[index][0].replace('.txt',''):
        title = test_lists[index][0].replace('.txt','')
        recommend1 = "%s.0000%d"%(genre[answer[1][1] // 10], answer[1][1] % 10)
        recommend2 = "%s.0000%d"%(genre[answer[2][1] // 10], answer[2][1] % 10)
        recommend3 = "%s.0000%d"%(genre[answer[3][1] // 10], answer[3][1] % 10)
        accuracy = max(match_prob, answer[0][0] / len(train_X))
    else:
        # 녹음파일 fingerprint가 너무 적거나 정확도가 ml보다 떨어지면 ml 모델 채택
        if len(rec_finger) < len(samples) // 11025 or match_prob < answer[0][0] / len(train_X): 
            title = "%s.0000%d"%(genre[answer[0][1] // 10], answer[0][1] % 10)
            recommend1 = "%s.0000%d"%(genre[answer[1][1] // 10], answer[1][1] % 10)
            recommend2 = "%s.0000%d"%(genre[answer[2][1] // 10], answer[2][1] % 10)
            if recommend1 != test_lists[index][0].replace('.txt','') and recommend2 != test_lists[index][0].replace('.txt',''):
                recommend3 = test_lists[index][0].replace('.txt','')
            else:
                recommend3 = "%s.0000%d"%(genre[answer[3][1] // 10], answer[3][1] % 10)
            accuracy = answer[0][0] / len(train_X)
        else:
            title = test_lists[index][0].replace('.txt','') # fingerprint 채택
            recommend1 = "%s.0000%d"%(genre[answer[0][1] // 10], answer[0][1] % 10)
            recommend2 = "%s.0000%d"%(genre[answer[1][1] // 10], answer[1][1] % 10)
            recommend3 = "%s.0000%d"%(genre[answer[2][1] // 10], answer[2][1] % 10)
            accuracy = answer[0][0] / len(train_X)

    # 반환 기본 틀은 바뀌면 안 됩니다.
    # key 6개('name': string, 'recommend1': string, 'recommend2': string,
    # 'recommend3': string, 'accuracy': float, , 'time': float)
    return jsonify({
        'name': title,
        'recommend1': recommend1,
        'recommend2': recommend2,
        'recommend3': recommend3, 
        'accuracy': accuracy,
        'time': time.time() - start,
    })

# def stop_local():
#     func = request.environ.get('werkzeug.server.shutdown')
#     if func is None:
#         raise RuntimeError('Not running with the Werkzeug Server')
#     func()