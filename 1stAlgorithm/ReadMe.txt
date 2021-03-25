필요한 모듈
numpy, wave, math, os

알고리즘 순서

구현된 것 :
1. wav파일 가져오기
2. 44100Hz를 11025Hz로 다운샘플링 (데이터 크기를 줄이기 위함)
3. 탭 1024인 hammaing window로 시간영역을 자름(주파수 왜곡 최소화)
4. 각 구간에 대해 FFT 적용한 후 시간 정보도 기록
5. 해당 음원의 전영역에 걸친 저주파(512Hz 미만)의 평균 크기를 구함 (혹여나 더욱 세분화된 저주파 리스트가 필요할 수 있을까 구현했지만 주석에 둠)
6. 저주파 평균 크기에 보정값(현재 1.2)을 곱한 후, 이 값보다 큰 주파수 영역 정보와 시간 정보만 가져옴
7. 임의의 주파수와 또다른 주파수 사이의 offset(최대 15)을 기록하여 데이터 저장

구현 해야할 것 :
8. 녹음된(임의로 잘라진) 음원과 저장된 데이터 비교하여 찾기

구현되면 좋을 것:
1. 저장 데이터를 16진법 hash로 암호화(데이터 크기를 획기적으로 줄임)
2. wav 파일 말고 mp3 파일을 불러오기(현 모듈은 mp3를 불러올 수 없어서 음원 용량이 큼)

참고문헌
http://coding-geek.com/how-shazam-works/ (알고리즘 1~6)
https://www.toptal.com/algorithms/shazam-it-music-processing-fingerprinting-and-recognition
https://github.com/worldveil/dejavu (알고리즘 7,8)