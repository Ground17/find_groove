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
import data_process

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
    params = request.get_json()
    # ai: ML, DL 사용 여부
    ai = params['ai'] 

    # samples: 11025Hz로 샘플링된 float 형식 4초 분량 녹음 데이터
    # 값 범위: (-1, 1)
    # 길이: 44100 (11025 * 4)
    samples = params['samples']

    ### 임시 테스트 wav 파일 생성 코드 ###
    import wave
    import struct
    wav_file = wave.open('./static/ai_inputs/test/100_4.wav', mode='wb') # 91_1 ~ 100_3
    wav_file.setparams((1, 2, 11025, 44100, "NONE", "not compressed"))

    amp = 64000.0
    for s in samples:
        # write the audio frames to file
        wav_file.writeframes(struct.pack('h', int(s * amp / 2)))

    wav_file.close()
    #####################################

    if ai:
        # colab에서 훈련시킨 tf 모델 이식
        mlp_vote = tf.keras.models.load_model('./static/models/mlp_vote')
        cnn_vote = tf.keras.models.load_model('./static/models/cnn_vote')
        cnn_rnn = tf.keras.models.load_model('./static/models/cnn_rnn')

        # mlp_vote.summary()

        # 반환 기본 틀은 바뀌면 안 됩니다.
        # key 4개('message': string, 'code': int, 'name': string, 'accuracy': float, 'time': float)
        return jsonify({
            'message': 'success!',
            'code': 200,
            'name': 'temp',
            'accuracy': 0.5,
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
    if max_value > 0:
        print("count:", max_value)
        print("result:", test_lists[index][0].replace('.txt','.wav'))
    else:
        print("result: None")

    # 반환 기본 틀은 바뀌면 안 됩니다.
    # key 4개('message': string, 'code': int, 'name': string, 'accuracy': float)
    return jsonify({
        'message': 'success!',
        'code': 200,
        'name': test_lists[index][0].replace('.txt','.wav'),
        'accuracy': 0.5,
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
    app.run(host='0.0.0.0', port=8080, debug=True) # 왠만하면 바꾸지 말아주세요
# [END gae_python3_render_template]
# [END gae_python38_render_template]
