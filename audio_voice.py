import librosa
import wave
import time
import os
import re
import sys
import random
import numpy as np
import matplotlib.pyplot as plt


class AudioVoice:
    """
    根据音频节奏筛选片段
    """

    def __init__(self, file):
        self.cvSave = True
        self.randomClip = False
        self.start = time.time()
        self.delFilesList = []
        self.Movie = file
        directory = os.path.split(file)[0]
        self.bgmPath = os.path.join(directory, "Auto_Cut_BGM")
        self.bgmPath = r"F:\Alan\Music\AutoCutBGM"
        name = os.path.splitext(file)[0]
        self.name = os.path.basename(name)
        self.cutPath = os.path.join(directory, "cut_video")
        self.videoPath = os.path.join(self.cutPath, self.name)
        self.Audio = os.path.join(directory, self.name + ".wav")
        self.saveNumber = 1
        self.video_splt_time = []
        self.save_filename_list = []
        self.first_video_audio = True

    def __del__(self):
        try:
            print("used time duration:{}s".format(time.time() - self.start))
            self.delFilesList += self.save_filename_list
            for file in self.delFilesList:
                os.remove(file)
        except Exception as e:
            print("__del__ error:", e)

    def audio_auto_cut(self):
        # self.video2audio(self.Movie)
        self.audio_get()
        self.audioDigital(self.Movie)
        if self.save_filename_list:
            self.video_concat(self.videoPath)

    def audio_get(self):
        if not os.path.exists(self.bgmPath):
            os.mkdir(self.bgmPath)
            print("pls add bgm to the folder:%s" % self.bgmPath)
        bgm_lst = []
        for bgm in os.listdir(self.bgmPath):
            bgm = os.path.join(self.bgmPath, bgm)
            bgm_lst.append(bgm)
        random.shuffle(bgm_lst)
        bgm = bgm_lst[0]
        print("choosed the bgm by freedom:", bgm)
        y, sr = librosa.load(bgm, sr=None)
        self.outpuDuration = librosa.get_duration(y=y, sr=sr)
        self.bgm = bgm

    def audio2dataByRosa(self, file):
        y, sr = librosa.load(file, sr=None)
        wav_time = np.arange(0, len(y)) * (1.0 / sr)
        mcff = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=1)
        self.framerate = sr
        self.nframes = len(y)
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

    def audioDigital(self, audio):
        audioTime, waveData = self.audio2dataByRosa(audio)
        np.abs(waveData, out=waveData)
        # 减小平均数据量
        time_arr = np.array([])
        speed_arr = np.array([])
        split_time = 2
        split_frame = int(self.framerate * split_time)
        frame = 0
        while frame < self.nframes:
            t = audioTime[frame]
            speed = np.max(waveData[frame: frame + split_frame])
            frame += split_frame
            time_arr = np.append(time_arr, t)
            speed_arr = np.append(speed_arr, speed)
        speed_arr = speed_arr / np.max(speed_arr)
        # 筛选符合时间段
        clips = []
        speed_cut = 1.0
        while True:
            time_sum = 0
            time_select = time_arr[np.where(speed_arr > speed_cut)[0]]
            time_cut_list = np.split(
                time_select, np.where(np.diff(time_select) != split_time)[0] + 1
            )
            for clip in time_cut_list:
                if len(clip) > 1:
                    time_sum += clip[-1] - clip[0]
                    clips.append(clip)
            if time_sum > self.outpuDuration:
                print("bgm duration:", self.outpuDuration)
                print("sum of selected clips time:", time_sum)
                break
            else:
                if speed_cut < 0:
                    break
                speed_cut -= 0.05
                clips = []
        bar = self.progress_bar(clips[-1][0])
        for clip in clips:
            # print("clip:",clip)
            bar.update(clip[0])
            self.cut_video(self.Movie, clip[0], clip[-1], cvSave=self.cvSave)
        bar.finish()
        # print(self.video_splt_time)


if __name__ == "__main__":
    pass
