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

# model = (tf.keras.models.load_model('./static/models/cnn_vote_best_total.h5'))
app = Flask(__name__)
ready = False

@app.route('/')
def root():
    # For the sake of example, use static information to inflate the template.
    # This will be replaced with real information in later steps.
    dummy_times = [datetime.datetime(2021, 10, 8, 23, 59, 59)]

    return render_template('index.html', times=dummy_times)

@app.route('/make')
def make_fingerprint():
    # ongoing...
    return jsonify({})

# @app.route('/search', methods=['POST'])
# def search():
#     start = time.time()
#     # f = request.files['file']
#     # f.save('./files/' + secure_filename(f.filename))

#     params = request.get_json()

#     # samples: 11025Hz로 샘플링된 float 형식 4초 분량 녹음 데이터
#     # 값 범위: (-1, 1)
#     # 길이: 44100 (11025 * 4)
#     samples = params['samples']

# # =================================================================
#     #임시 wav파일 저장 - 수종

#     # wav_file = wave.open('./test_data/test00009.wav', "w")
#     # data_size = len(samples)
#     # nchannels = 1
#     # sampwidth = 2
#     # framerate = 44100/4
#     # nframes = data_size
#     # comptype = "NONE"
#     # compname = "not compressed"

#     # wav_file.setparams((nchannels, sampwidth, framerate, nframes,
#     # comptype, compname))

#     # for s in samples:
#     #     wav_file.writeframes(struct.pack('h',int(32000*s)))

#     # wav_file.close()
# # =====================================================================
#     ### 임시 테스트 wav 파일 생성 코드 ###
#     # import wave
#     # import struct
#     # wav_file = wave.open('./static/ai_inputs/test/1-0.wav', mode='wb') # 91_1 ~ 100_3
#     # wav_file.setparams((1, 2, 11025, 44100, "NONE", "not compressed"))

#     # amp = 64000.0
#     # for s in samples:
#     #     # write the audio frames to file
#     #     wav_file.writeframes(struct.pack('h', int(s * amp / 2)))

#     # wav_file.close()
#     # return None
#     #####################################

#     # 1. ml model
#     genre = [
#         "blues",
#         "classical",
#         "country",
#         "disco",
#         "hiphop",
#         "jazz",
#         "metal",
#         "pop",
#         "reggae",
#         "rock",
#         ]
#     array_X = []
#     ffts = data_process.spectrogram(samples) # (length, 512) => (512, 30)
#     temp30 = []
#     for m in range(len(ffts)): # 30개씩 쌓기
#         for n in range(30):
#             if m + n < len(ffts):
#                 temp30.append(ffts[m + n])      
#         if len(temp30) == 30:
#             array_X.append(temp30)
#             temp30 = []

#     train_X = np.array(array_X)

#     for i in range(len(train_X)): # 데이터 정규화
#         for j in range(len(train_X[i])):
#             if np.std(train_X[i, j]) == 0:
#                 continue
#             train_X[i, j] = (train_X[i, j] - np.mean(train_X[i, j])) / np.std(train_X[i, j])

#     train_X = np.swapaxes(train_X, 1, 2)

#     train_X = train_X[..., np.newaxis]
#     count = [0 for _ in range(100)]
#     predictions = model.predict(train_X)
#     temp = np.argmax(predictions, axis=1)
#     for index in temp:
#         count[index] += 1

#     answer = []
#     for i, c in enumerate(count):
#         answer.append((c, i))
#     answer.sort(reverse=True)

#     # 2. fingerprint
#     rec_peaks = spectrogram.spectrogram(samples)     #녹음/일부 음원 스펙트로그램 적용
#     rec_finger = compare.rec_fingerprints(rec_peaks)    #녹음된 음원 지문을 기록
#     index = -1
#     max_value = 0
#     for i, v in enumerate(test_lists):
#         file_name, test_list = v
#         offset = compare.compare(test_list, rec_finger)  #비교 음원의 offset 차이의 최빈값을 구함
#         # if offset > 0:
#         #     print(file_name, offset)
#         if max_value < offset:
#             max_value = offset
#             index = i

#     # if max_value > 0:
#     #     print("count:", max_value)
#     #     print("result:", test_lists[index][0].replace('.txt','.wav'))
#     #     print("time:", time.time() - start)
#     # else:
#     #     print("result: None")
#     #     print("time: ", time.time() - start)

#     match_prob = max_value / len(rec_finger)
#     # if match_prob > 0.05:
#     #     print("result:", test_lists[index][0].replace('.txt',''))
#     #     print("probability:", match_prob * 100,"%")
#     #     print("time:", time.time() - start)

#     # fingerprint, model에서 나온 모든 정보 정리
#     title = ""
#     recommend1 = ""
#     recommend2 = ""
#     recommend3 = ""
#     accuracy = 0.0

#     if "%s.0000%d"%(genre[answer[0][1] // 10], answer[0][1] % 10) == test_lists[index][0].replace('.txt',''):
#         title = test_lists[index][0].replace('.txt','')
#         recommend1 = "%s.0000%d"%(genre[answer[1][1] // 10], answer[1][1] % 10)
#         recommend2 = "%s.0000%d"%(genre[answer[2][1] // 10], answer[2][1] % 10)
#         recommend3 = "%s.0000%d"%(genre[answer[3][1] // 10], answer[3][1] % 10)
#         accuracy = max(match_prob, answer[0][0] / len(train_X))
#     else:
#         # 녹음파일 fingerprint가 너무 적거나 정확도가 ml보다 떨어지면 ml 모델 채택
#         if len(rec_finger) < len(samples) // 11025 or match_prob < answer[0][0] / len(train_X): 
#             title = "%s.0000%d"%(genre[answer[0][1] // 10], answer[0][1] % 10)
#             recommend1 = "%s.0000%d"%(genre[answer[1][1] // 10], answer[1][1] % 10)
#             recommend2 = "%s.0000%d"%(genre[answer[2][1] // 10], answer[2][1] % 10)
#             if recommend1 != test_lists[index][0].replace('.txt','') and recommend2 != test_lists[index][0].replace('.txt',''):
#                 recommend3 = test_lists[index][0].replace('.txt','')
#             else:
#                 recommend3 = "%s.0000%d"%(genre[answer[3][1] // 10], answer[3][1] % 10)
#             accuracy = answer[0][0] / len(train_X)
#         else:
#             title = test_lists[index][0].replace('.txt','') # fingerprint 채택
#             recommend1 = "%s.0000%d"%(genre[answer[0][1] // 10], answer[0][1] % 10)
#             recommend2 = "%s.0000%d"%(genre[answer[1][1] // 10], answer[1][1] % 10)
#             recommend3 = "%s.0000%d"%(genre[answer[2][1] // 10], answer[2][1] % 10)
#             accuracy = answer[0][0] / len(train_X)

#     # 반환 기본 틀은 바뀌면 안 됩니다.
#     # key 6개('name': string, 'recommend1': string, 'recommend2': string,
#     # 'recommend3': string, 'accuracy': float, , 'time': float)
#     return jsonify({
#         'name': title,
#         'recommend1': recommend1,
#         'recommend2': recommend2,
#         'recommend3': recommend3, 
#         'accuracy': accuracy,
#         'time': time.time() - start,
#         })

def run_flask(port=8080, local=True):
    app.run(host='127.0.0.1' if local else '0.0.0.0', port=port, debug=True)

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.

    app.run(host='0.0.0.0', port=8080, debug=True)

    # 성능 테스트용 코드
    # path = './static/ai_inputs/test'
    # music_list = os.listdir(path)

    # for b in music_list:
    #     print(b)
    #     print("")
    #     start = time.time()
    #     rec_peaks = spectrogram.spectrogram(path + "/" + b)     #녹음/일부 음원 스펙트로그램 적용
    #     rec_finger = compare.rec_fingerprints(rec_peaks)    #녹음된 음원 지문을 기록
    #     index = -1
    #     max_value = 0
    #     for i, v in enumerate(test_lists):
    #         file_name, test_list = v
    #         offset = compare.compare(test_list, rec_finger)  #비교 음원의 offset 차이의 최빈값을 구함
    #         # if offset > 0:
    #         #     print(file_name, offset)
    #         if max_value < offset:
    #             max_value = offset
    #             index = i

    #     match_prob = max_value / len(rec_finger)
    #     if match_prob > 0.05:
    #         print("count:", max_value)
    #         print("result:", test_lists[index][0].replace('.txt',''))
    #         print("probability:", match_prob * 100,"%")
    #         print("time:", time.time() - start)
    #     else:
    #         print("time:", time.time() - start)
        
    #     # genre = {
    #     #     "blues": 0,
    #     #     "classical": 1,
    #     #     "country": 2,
    #     #     "disco": 3,
    #     #     "hiphop": 4,
    #     #     "jazz": 5,
    #     #     "metal": 6,
    #     #     "pop": 7,
    #     #     "reggae": 8,
    #     #     "rock": 9,
    #     #     }
    #     print("")
    #     start = time.time()

    #     genre = [
    #         "blues",
    #         "classical",
    #         "country",
    #         "disco",
    #         "hiphop",
    #         "jazz",
    #         "metal",
    #         "pop",
    #         "reggae",
    #         "rock",
    #         ]
    #     array_X = []
    #     ffts = data_process.spectrogram(path + "/" + b) # (length, 512) => (512, 30)
    #     temp30 = []
    #     for m in range(len(ffts)): # 30개씩 쌓기
    #         for n in range(30):
    #             if m + n < len(ffts):
    #                 temp30.append(ffts[m + n])      
    #         if len(temp30) == 30:
    #             array_X.append(temp30)
    #             temp30 = []

    #     train_X = np.array(array_X)

    #     for i in range(len(train_X)): # 데이터 정규화
    #         for j in range(len(train_X[i])):
    #             if np.std(train_X[i, j]) == 0:
    #                 continue
    #             train_X[i, j] = (train_X[i, j] - np.mean(train_X[i, j])) / np.std(train_X[i, j])

    #     train_X = np.swapaxes(train_X, 1, 2)

    #     train_X = train_X[..., np.newaxis]
    #     count = [0 for _ in range(100)]
    #     predictions = model.predict(train_X)
    #     temp = np.argmax(predictions, axis=1)
    #     for index in temp:
    #         count[index] += 1

    #     answer = []
    #     for i, c in enumerate(count):
    #         answer.append((c, i))
    #     answer.sort(reverse=True)

    #     print("count:", answer[0][0])
    #     print("result:", "%s.0000%d"%(genre[answer[0][1] // 10], answer[0][1] % 10))
    #     print("result:", "%s.0000%d"%(genre[answer[1][1] // 10], answer[1][1] % 10))
    #     print("result:", "%s.0000%d"%(genre[answer[2][1] // 10], answer[2][1] % 10))
    #     print("result:", "%s.0000%d"%(genre[answer[3][1] // 10], answer[3][1] % 10))
    #     print("probability:", answer[0][0] / len(train_X) * 100, "%")
    #     print("time:", time.time() - start)
    #     print("")

# [END gae_python3_render_template]
# [END gae_python38_render_template]
