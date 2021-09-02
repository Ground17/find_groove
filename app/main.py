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

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


@app.route('/')
def root():
    # For the sake of example, use static information to inflate the template.
    # This will be replaced with real information in later steps.
    dummy_times = [datetime.datetime(2018, 1, 1, 10, 0, 0),
                   datetime.datetime(2018, 1, 2, 10, 30, 0),
                   datetime.datetime(2018, 1, 3, 11, 0, 0),
                   ]

    return render_template('index.html', times=dummy_times)

@app.route('/search', methods=['POST'])
def search():
    params = request.get_json()
    # ai: ML, DL 사용 여부
    ai = params['ai'] 

    # samples: 11025Hz로 샘플링된 float 형식 4초 분량 녹음 데이터
    # 값 범위: (-1, 1)
    # 길이: 44100 (11025 * 4)
    samples = params['samples']
    if ai:
        # colab에서 훈련시킨 tf 모델 이식
        return jsonify({'message': 'success!', 'code': 200, 'name': None, 'accuracy': 0})

    ### 이 부분부터 수정해주시면 됩니다 ###

    return jsonify({'message': 'success!', 'code': 200, 'name': None, 'accuracy': 0})


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='0.0.0.0', port=8080, debug=True)
# [END gae_python3_render_template]
# [END gae_python38_render_template]
