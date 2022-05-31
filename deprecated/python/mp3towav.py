from pydub import AudioSegment
import os

def mp3towav():
    path = '../data/input_mp3/'
    music_list = os.listdir(path)
    for k in music_list:

        # files                                                                       
        src = '../data/input_mp3/'+k
        dst = '../data/output_wav/'+k.replace('.mp3','.wav')

        # convert mp3 to wav
        # 사용 전 ffmpeg 다운로드, 환경변수 설정                                                         
        audSeg = AudioSegment.from_mp3(src)
        audSeg.export(dst, format="wav")
if __name__ == "__main__":
    mp3towav()