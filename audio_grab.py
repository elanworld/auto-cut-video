import time

import numpy as np
from pyaudio import PyAudio, paInt16

framerate = 16000
NUM_SAMPLES = 100
channels = 1
sampwidth = 2
TIME = 10


def get_input():
    p = PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    devices = []
    for i in range(0, numdevices):
        devices.append(p.get_device_info_by_host_api_device_index(0, i))
        print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
    return devices[1]


@DeprecationWarning
def frame_deal(data):
    """
    信号反向处理
    :param data:
    :return:
    """
    new_data = b""
    for c in data:
        _n = -(int(c) - 128) + 128
        b = bytes(_n)
        new_data += b
    return new_data


def noise_replay():
    """
    实时播放音波
    误差距离~=5e-5*343=0.017m
    :return:
    """
    pa = PyAudio()
    stream = pa.open(format=paInt16, channels=1,
                     rate=framerate, input=True,
                     frames_per_buffer=NUM_SAMPLES, input_device_index=1)
    out_stream = pa.open(format=paInt16, channels=1,
                         rate=framerate, output=True, output_device_index=5)
    count = 0
    while count < TIME * 200000:
        start = time.clock()
        data = stream.read(NUM_SAMPLES)
        fromstring = np.fromstring(data, dtype=np.int16)
        negative = np.negative(fromstring)
        negative_data = negative.tostring()
        out_stream.write(negative_data)
        print(time.clock() - start)
        count += 1
        print('.')


if __name__ == '__main__':
    get_input()
    noise_replay()
