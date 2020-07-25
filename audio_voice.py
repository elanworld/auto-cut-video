import librosa
import wave
import numpy as np
import matplotlib.pyplot as plt


class AudioVoice:
    def audio2dataByRosa(self, file):
        y, sr = librosa.load(file, sr=None)
        wav_time = np.arange(0, len(y)) * (1.0 / sr)
        mcff = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=1)
        self.framerate = sr
        self.nframes = len(y)
        # self.matplot(mcff[0])
        # self.matplot(y)
        return wav_time, y

    def audio2data(self, wav):
        f = wave.open(wav, "rb")
        params = f.getparams()
        nchannels, sampwidth, self.framerate, self.nframes = params[:4]
        strData = f.readframes(self.nframes)
        f.close()
        waveData = np.fromstring(strData, dtype=np.short)
        waveData.shape = -1, 2
        waveData = waveData.T
        waveData = waveData[0]
        audioTime = np.arange(0, self.nframes) * (1.0 / self.framerate)
        return audioTime, waveData

    def matplot(self, y_lst, x_lst=None):
        # plot audio character
        if x_lst is None:
            x_lst = range(len(y_lst))
        plt.plot(x_lst, y_lst)
        plt.show()


if __name__ == "__main__":
    file = r"F:\Alan\Videos\电影\aa.mp4"
    av = AudioVoices().getFrame(file)
