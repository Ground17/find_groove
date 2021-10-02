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

from flask import Flask, render_template, request, jsonify
import compare
import spectrogram
import data_process
import os
import wave
import struct
from werkzeug.utils import secure_filename

app = Flask(__name__)


@app.route('/')
def root():
    # For the sake of example, use static information to inflate the template.
    # This will be replaced with real information in later steps.
    dummy_times = [datetime.datetime(2021, 9, 3, 23, 59, 59)]

    return render_template('index.html', times=dummy_times)

@app.route('/search', methods=['POST'])
def search():
    # f = request.files['file']
    # f.save('./files/' + secure_filename(f.filename))

    params = request.get_json()
    # ai: ML, DL 사용 여부
    ai = params['ai'] 

    # samples: 11025Hz로 샘플링된 float 형식 4초 분량 녹음 데이터
    # 값 범위: (-1, 1)
    # 길이: 44100 (11025 * 4)
    samples = params['samples']

    #녹음된 음원을 파일로 저장할 때 활성화하면 됩니다.

    wav_file = wave.open('./test_data/test00009.wav', "w")
    data_size = len(samples)
    nchannels = 1
    sampwidth = 2
    framerate = 44100/4
    nframes = data_size
    comptype = "NONE"
    compname = "not compressed"

    wav_file.setparams((nchannels, sampwidth, framerate, nframes,
    comptype, compname))

    for s in samples:
        wav_file.writeframes(struct.pack('h',int(32000*s)))

    wav_file.close()

    if ai:
        # colab에서 훈련시킨 tf 모델 이식

        # 반환 기본 틀은 바뀌면 안 됩니다.
        # key 4개('message': string, 'code': int, 'name': string, 'accuracy': float, 'time': float)
        return jsonify({
            'message': 'success!',
            'code': 200,
            'name': 'temp',
            'accuracy': 0.5,
            'time': 0.0
            })

    ### 이 부분부터 수정해주시면 됩니다 ###
    start = time.time()
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
            'accuracy': match_prob
            })
    else:
        print("result: None")
        print("time: ", time.time() - start)

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
            'accuracy': 0.5,
            'time': 0.0
            })

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='0.0.0.0', port=8080, debug=True) # 왠만하면 바꾸지 말아주세요
# [END gae_python3_render_template]
# [END gae_python38_render_template]
