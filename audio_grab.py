import time

from pyaudio import PyAudio, paInt16

framerate = 16000
NUM_SAMPLES = 50
channels = 1
sampwidth = 2
TIME = 10


def noise_replay():
    """
    实时播放音波
    误差距离~=5e-5*343=0.017m
    :return:
    """
    pa = PyAudio()
    stream = pa.open(format=paInt16, channels=1,
                     rate=framerate, input=True,
                     frames_per_buffer=NUM_SAMPLES)
    out_stream = pa.open(format=paInt16, channels=1,
                         rate=framerate, output=True)
    count = 0
    while count < TIME * 200000:  # 控制录音时间
        start = time.clock()
        string_audio_data = stream.read(NUM_SAMPLES)
        out_stream.write(string_audio_data)
        print(time.clock() - start)
        count += 1
        print('.')


if __name__ == '__main__':
    noise_replay()
