import multiprocessing
import time

import numpy as np
from pyaudio import PyAudio, paInt16


class NoiseBlance:
    def __init__(self):
        self.framerate = 16000
        self.NUM_SAMPLES = 100

        self.q = multiprocessing.Queue()

    def get_input(self):
        p = PyAudio()
        info = p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        devices = []
        for i in range(0, numdevices):
            devices.append(p.get_device_info_by_host_api_device_index(0, i))
            print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
        return devices[1]

    @DeprecationWarning
    def frame_deal(self, data):
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

    def noise_record(self):
        pa = PyAudio()
        stream = pa.open(format=paInt16, channels=1,
                         rate=self.framerate, input=True,
                         frames_per_buffer=self.NUM_SAMPLES, input_device_index=1)
        while True:
            data = stream.read(self.NUM_SAMPLES)
            self.q.put(data)

    def noise_replay(self):
        """
        实时播放音波
        误差距离~=5e-5*343=0.017m
        :return:
        """
        pa = PyAudio()
        out_stream = pa.open(format=paInt16, channels=1,
                             rate=self.framerate, output=True, output_device_index=5)
        while True:
            start = time.clock()
            fromstring = np.fromstring(self.q.get(), dtype=np.int16)
            negative = np.negative(fromstring)
            negative_data = negative.tostring()
            out_stream.write(negative_data)
            print(time.clock() - start)

    def run(self):
        multiprocessing.Process(target=self.noise_replay).start()
        multiprocessing.Process(target=self.noise_record).start()


if __name__ == '__main__':
    NoiseBlance().run()
