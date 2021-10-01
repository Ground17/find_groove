# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python38_render_template]
# [START gae_python3_render_template]
import datetime
import time

from flask import Flask, render_template, request, jsonify, url_for
import compare
import spectrogram
import tensorflow as tf
import numpy as np
import data_process
import os
import wave
import pickle
import data_process
from scipy.stats import mode

app = Flask(__name__)

@app.route('/')
def root():
    # For the sake of example, use static information to inflate the template.
    # This will be replaced with real information in later steps.
    dummy_times = [datetime.datetime(2021, 9, 3, 23, 59, 59)]

    return render_template('index.html', times=dummy_times)

@app.route('/search', methods=['POST'])
def search():
    start = time.time()
    # f = request.files['file']
    # f.save('./files/' + secure_filename(f.filename))

    params = request.get_json()
    # ai: ML, DL 사용 여부
    ai = params['ai'] 

    # samples: 11025Hz로 샘플링된 float 형식 4초 분량 녹음 데이터
    # 값 범위: (-1, 1)
    # 길이: 44100 (11025 * 4)
    samples = params['samples']

    ### 임시 테스트 wav 파일 생성 코드 ###
    # import wave
    # import struct
    # wav_file = wave.open('./static/ai_inputs/test/100_4.wav', mode='wb') # 91_1 ~ 100_3
    # wav_file.setparams((1, 2, 11025, 44100, "NONE", "not compressed"))

    # amp = 64000.0
    # for s in samples:
    #     # write the audio frames to file
    #     wav_file.writeframes(struct.pack('h', int(s * amp / 2)))

    # wav_file.close()
    #####################################

    if ai:
        # colab에서 훈련시킨 tf 모델 이식
        mlp_vote = tf.keras.models.load_model('./static/models/mlp_vote.h5')
        cnn_vote = tf.keras.models.load_model('./static/models/cnn_vote.h5')
        cnn_rnn = tf.keras.models.load_model('./static/models/cnn_rnn.h5')

        with open('./static/variables/title', 'rb') as f:
            title = pickle.load(f)
        array_X = []
        ffts = data_process.spectrogram(samples) # (length, 512) => (512, 10)
        for m in range(len(ffts)): # 10개씩 쌓기
            temp10 = []
            for n in range(10):
                if m + n < len(ffts):
                    temp10.append(ffts[m + n])
            if len(temp10) == 10:
                array_X.append(temp10)
                temp10 = []
        train_X = np.array(array_X)

        for i in range(len(train_X)):
            for j in range(len(train_X[i])):
                if np.std(train_X[i, j]) == 0:
                    continue
                train_X[i, j] = (train_X[i, j] - np.mean(train_X[i, j])) / np.std(train_X[i, j])
                

        train_X = np.swapaxes(train_X, 1, 2)

        train_X = train_X[..., np.newaxis]

        predictions = cnn_vote.predict(train_X)

        # 반환 기본 틀은 바뀌면 안 됩니다.
        # key 4개('message': string, 'code': int, 'name': string, 'accuracy': float, 'time': float)
        return jsonify({
            'message': 'success!',
            'code': 200,
            'name': title[mode(np.argmax(predictions, axis=1))[0][0]],
            'accuracy': 0.0,
            'time': time.time() - start
        })

    ### 이 부분부터 수정해주시면 됩니다 ###
    test_lists = compare.load_tuple()

    rec_peaks = spectrogram.spectrogram(samples)     #녹음/일부 음원 스펙트로그램 적용
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
        print("time:", time.time() - start)

        # 반환 기본 틀은 바뀌면 안 됩니다.
        # key 4개('message': string, 'code': int, 'name': string, 'accuracy': float)
        
        return jsonify({
            'message': 'success!',
            'code': 200,
            'name': test_lists[index][0].replace('.txt','.wav'),
            'accuracy': match_prob,
            'time': time.time() - start
            })
    else:
        print("result: None")

    # if max_value > 0:
    #     print("count:", max_value)
    #     print("result:", test_lists[index][0].replace('.txt','.wav'))
    #     print("time:", time.time() - start)
    # else:
    #     print("result: None")
    #     print("time: ", time.time() - start)

    # 반환 기본 틀은 바뀌면 안 됩니다.
    # key 4개('message': string, 'code': int, 'name': string, 'accuracy': float)

    return jsonify({
        'message': 'failed!',
        'code': 200,
        'name': 'None',
        'accuracy': 0.0,
        'time': time.time() - start
        })

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    # app.run(host='0.0.0.0', port=8080, debug=True) # 왠만하면 바꾸지 말아주세요
    mlp_vote = tf.keras.models.load_model('./static/models/mlp_vote.h5')
    cnn_vote = tf.keras.models.load_model('./static/models/cnn_vote.h5')
    cnn_rnn = tf.keras.models.load_model('./static/models/cnn_rnn.h5')
    with open('./static/variables/title', 'rb') as f:
        title = pickle.load(f)
    path = './static/ai_inputs/test'
    music_list = os.listdir(path)

    # #1 - mlp_vote
    # for b in music_list:
    #     array_X = []
    #     genre_path = path + '/' + b
    #     ffts = data_process.spectrogram(genre_path) # (length, 512)
    #     for m in range(len(ffts)): # 10개씩 쌓기
    #         array_X.append(ffts[m])

    #     train_X = np.array(array_X)

    #     for i in range(len(train_X)):
    #         if np.std(train_X[i]) == 0:
    #             continue
    #         train_X[i] = (train_X[i] - np.mean(train_X[i])) / np.std(train_X[i])
        
    #     predictions = mlp_vote.predict(train_X)
    #     print(b)
    #     print(title[mode(np.argmax(predictions, axis=1))[0][0]])
        
    #2 - cnn_vote
    for b in music_list:
        array_X = []
        genre_path = path + '/' + b
        ffts = data_process.spectrogram(genre_path) # (length, 512) => (512, 10)
        for m in range(len(ffts)): # 10개씩 쌓기
            temp10 = []
            for n in range(10):
                if m + n < len(ffts):
                    temp10.append(ffts[m + n])
            if len(temp10) == 10:
                array_X.append(temp10)
                temp10 = []
        train_X = np.array(array_X)

        for i in range(len(train_X)):
            for j in range(len(train_X[i])):
                if np.std(train_X[i, j]) == 0:
                    continue
                train_X[i, j] = (train_X[i, j] - np.mean(train_X[i, j])) / np.std(train_X[i, j])
                

        train_X = np.swapaxes(train_X, 1, 2)

        train_X = train_X[..., np.newaxis]

        predictions = cnn_vote.predict(train_X)
        print(b)
        print(title[mode(np.argmax(predictions, axis=1))[0][0]])

    # #3 - cnn_rnn
    # array_X = []
    # for b in music_list:
    #     genre_path = path + '/' + b
    #     ffts = data_process.spectrogram(genre_path) # (length, 512) => (3, 512, 10)
    #     temp = []
    #     temp3 = []
    #     temp10 = []
    #     for m in range(len(ffts)):
    #         temp10.append(ffts[m])
    #         if len(temp10) == 10:
    #             temp3.append(temp10)
    #             temp10 = []
    #         if len(temp3) == 3:
    #             array_X.append(temp3)
    #             temp3 = []

    #             train_X = np.swapaxes(np.array(array_X), 2, 3)

    #     # 스케일 조정 - mean: 0, std: 1
    #     for i in range(len(train_X)):
    #         for j in range(len(train_X[i])):
    #             if np.std(train_X[i, j]) == 0:
    #                 continue
    #             train_X[i, j] = (train_X[i, j] - np.mean(train_X[i, j])) / np.std(train_X[i, j])

    #     train_X = train_X[..., np.newaxis]
    #     predictions = cnn_rnn.predict(train_X)
    #     print(b)
    #     print(title[mode(np.argmax(predictions, axis=1))[0][0]])

# [END gae_python3_render_template]
# [END gae_python38_render_template]
