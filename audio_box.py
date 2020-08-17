import librosa
import wave
import numpy as np
from matplotlib import pyplot as plt


class AudioBox:
    def audio2dataByRosa(self, audio):
        y, sr = librosa.load(audio, sr=None)
        wav_time = np.arange(0, len(y)) * (1.0 / sr)
        self.mcff = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=1)
        self.framerate = sr
        self.nframes = len(y)
        return y, wav_time

    def audio2data(self, wav):
        f = wave.open(wav, "rb")
        params = f.getparams()
        nchannels, sampwidth, framerate, nframes = params[:4]
        strData = f.readframes(nframes)
        f.close()
        waveData = np.fromstring(strData, dtype=np.short)
        waveData.shape = -1, 2
        waveData = waveData.T
        waveData = waveData[0]
        audioTime = np.arange(0, nframes) * (1.0 / framerate)
        return waveData, audioTime

    def avg_data(self, data, ratio=10):
        size = len(data)
        new_data = []
        for i in range(0, size, ratio):
            sum_data = sum(data[i: i + ratio])
            clip = sum_data / ratio
            new_data.append(clip)
        return new_data

    def balance(self, data):
        max_data = max(data)
        percent = 1 / max_data
        for i in range(len(data)):
            data[i] *= percent
        return data

    def get_time(self, audio_data, duration):
        time = np.arange(0, len(audio_data)) * (duration / len(audio_data))
        return time

    """
    @:param data: need clip data
    @:param height: collecte data what is > height
    @:return index of collection data clips
    """

    def clip_data(self, data, height=0.2):
        if len(data) == 0:
            raise Exception("data is empty")
        height_list = []
        for i in range(len(data)):
            if data[i] > height:
                height_list.append(i)
        # add index of data to clips
        clips = []
        if len(height_list) == 0:
            return
        else:
            start = 0
            for i in range(len(height_list) - 1):
                if height_list[i + 1] - height_list[i] != 1:
                    clip = [height_list[start], height_list[i]]
                    start = i + 1
                    if clip[0] != clip[1]:
                        clips.append(clip)
            if height_list[-1] - height_list[-2] == 1 and len(height_list) > 2:
                clips.append([height_list[start], height_list[-1]])
            return clips

    def matplot(self, y_lst, x_lst=None):
        # plot audio character
        if x_lst is None:
            x_lst = range(len(y_lst))
        plt.plot(x_lst, y_lst)
        plt.show()
