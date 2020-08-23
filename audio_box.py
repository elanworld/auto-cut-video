import librosa
import wave
import numpy as np
from matplotlib import pyplot as plt


class AudioBox:
    def audio2data_rosa(self, audio):
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
        wave_data = np.fromstring(strData, dtype=np.short)
        wave_data.shape = -1, 2
        wave_data = wave_data.T
        wave_data = wave_data[0]
        audioTime = np.arange(0, nframes) * (1.0 / framerate)
        return wave_data, audioTime

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

    def time_get(self, audio_data, duration):
        time = np.arange(0, len(audio_data)) * (duration / len(audio_data))
        return time

    def clip_data(self, data, height=0.2):
        """
        @:param data: need clip data
        @:param height: collecte data what is > height
        @:return index of collection data clips
        """
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

    def time_edge_processs(self, time_clips, gap=0.5):
        """
        时间切片圆润处理
        :param time_clips: 时间切片list[list[1,2],...]
        :param gap: 圆润时间角度
        :return: 新的时间切片
        """
        for time in time_clips:
            if len(time) < 2:
                raise Exception("time list in time_clips is not complete")
        new_clips = [time_clips[0]]
        for i in range(1, len(time_clips)):
            before = new_clips[-1]
            after = time_clips[i]
            if after[0] - before[1] > gap:
                after = [after[0] - gap / 2, after[1] + gap / 2]
                new_clips.append(after)
            else:
                end = after[1] + gap / 2
                new_clips[-1][1] = end
        return new_clips

    def matplot(self, y_lst, x_lst=None):
        # plot audio character
        if x_lst is None:
            x_lst = range(len(y_lst))
        plt.plot(x_lst, y_lst)
        plt.show()
