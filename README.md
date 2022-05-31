# Find Groove
app/ 구글 앱엔진 웹 앱 배포용 (API 통신을 이용하여 서버에서 Python Flask 작동)

### repo structure
python/ : 스펙토그램, 핑거프린트 생성, mp3를 wav로 변환
csharp/ : for Unity (녹음 등)
data/ : 음악, 핑거프린트 저장 (데이터 경로: http://marsyas.info/downloads/datasets.html, 파일이 매우 커 git에는 업로드하지 않음, 테스트 시 따로 설치 권장)
*** data/ 디렉토리 위치는 변경될 수 있음 (ex. python 내부)

녹음 파일은 2초로 고정, 나머지 시간은 처리 시간

To do list
- [] 탐색 속도 높이는 알고리즘
- [] 녹음파일 정확도 향상
ML: https://colab.research.google.com/drive/1vWDSqXHt9nSvIsPM4ByT_7XvqIuwP1MB?usp=sharing

참고문헌
http://coding-geek.com/how-shazam-works/ (알고리즘 1~6)
https://www.toptal.com/algorithms/shazam-it-music-processing-fingerprinting-and-recognition
https://github.com/worldveil/dejavu (알고리즘 7,8)