import os
import sys
import re
import subprocess
import time
import cv2
import numpy as np


class CutMovie():
    # Auto cut video
    def __init__(self, file):
        self.cvSave = True
        self.randomClip = False
        self.start = time.time()
        self.delFilesList = []
        self.Movie = file
        dir = os.path.split(file)[0]
        self.bgmPath = os.path.join(dir, "Auto_Cut_BGM")
        self.bgmPath = r"F:\Alan\Music\AutoCutBGM"
        if len(sys.argv) >= 3:
            self.bgmPath = sys.argv[2]
            print("BGM path:", sys.argv[2])
        name = os.path.splitext(file)[0]
        self.name = os.path.basename(name)
        self.cutPath = os.path.join(dir, "cut_video")
        self.videoPath = os.path.join(self.cutPath, self.name)
        self.Audio = os.path.join(dir, self.name + ".wav")
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

    def save_ignor(
            self, frames=None, rate=None, startFrame=None, stopFrame=None
    ):
        if not os.path.exists(self.cutPath):
            os.mkdir(self.cutPath)
        if not os.path.exists(self.videoPath):
            os.mkdir(self.videoPath)
        if frames:
            duration = len(frames) / rate
        else:
            duration = (stopFrame - startFrame) / rate
        if duration < 0.3:
            # print("skip a small clip")
            return False
        return True

    def save_video(self, frames, rate, size):
        if not self.save_ignor(
                frames=frames, rate=rate, startFrame=None, stopFrame=None
        ):
            return
        self.video_splt_time.append(len(frames))
        save_filename = os.path.join(
            self.videoPath, self.name + "_" + str(self.saveNumber) + ".avi"
        )
        self.save_filename_list.append(save_filename)
        self.saveNumber += 1
        # print(save_filename)
        writer = cv2.VideoWriter()
        writer.open(
            save_filename, int(1145656920), rate, size, True
        )  # 参数2为avi格式的forucc，使用别的格式会导致转换出错
        for frame in frames:
            writer.write(frame)
        return True

    def save_video_with_ffmpeg(self, filename, startFrame=0, stopFrame=1, rate=24):
        if self.save_ignor(
                startFrame=startFrame,
                stopFrame=stopFrame,
                rate=rate):
            return
        self.video_splt_time.append([startFrame, stopFrame])
        ffmpegPath = "ffmpeg"
        save_filename = os.path.join(
            self.videoPath, self.name + "_" + str(self.saveNumber) + ".ts"
        )
        self.save_filename_list.append(save_filename)
        self.saveNumber += 1
        # print(save_filename)
        cmd = [
            ffmpegPath,
            "-y",
            "-ss",
            str(startFrame / float(rate)),
            "-t",
            str((stopFrame - startFrame) / float(rate)),
            "-i",
            filename,
            "-acodec",
            "copy",
            "-vcodec",
            "copy",
            "-vbsf",
            "h264_mp4toannexb",
            save_filename,
        ]
        cmd1 = [
            ffmpegPath,
            "-y",
            "-ss",
            str(startFrame / float(rate)),
            "-t",
            str((stopFrame - startFrame) / float(rate)),
            "-i",
            filename,
            "-an",
            "-vcodec",
            "copy",
            "-vbsf",
            "h264_mp4toannexb",
            save_filename,
        ]
        if not self.first_video_audio:
            import random

            if random.randint(0, 100) > 10:
                cmd = cmd1
        else:
            self.first_video_audio = False

        subprocess.call(cmd, stderr=subprocess.PIPE)
        cmd = " ".join(cmd)
        # print(cmd)

    def cut_video(self, filename, start, end, cvSave=True):
        # cut video to a clip what i want
        capture = cv2.VideoCapture(filename)
        if capture.isOpened():
            width = capture.get(int(cv2.CAP_PROP_FRAME_WIDTH))
            height = capture.get(int(cv2.CAP_PROP_FRAME_HEIGHT))
            size = (int(width), int(height))
            totalFrameNumber = capture.get(cv2.CAP_PROP_FRAME_COUNT)
            rate = capture.get(cv2.CAP_PROP_FPS)
            frameToStart = int(start * rate)
            frameToEnd = int(end * rate)
            capture.set(cv2.CAP_PROP_POS_FRAMES, frameToStart)
            currentFrame = frameToStart
            success, frame = capture.read()
            frames = []
            while currentFrame <= frameToEnd:
                currentImg = frame
                if cvSave:
                    frames.append(frame)
                success, frame = capture.read()
                if not success:
                    currentFrame += 1
                    continue
                currentFrame += 1
                lastImg = frame
                isSimilar = self.classify_pHash(currentImg, lastImg)
                if (not isSimilar) or (currentFrame >= frameToEnd):
                    if cvSave:
                        self.save_video(frames, rate, size)
                        frames = []
                    else:
                        self.save_video_with_ffmpeg(
                            filename, frameToStart, currentFrame, rate
                        )
                    frameToStart = currentFrame + 1
            capture.release()

    def writeF(self, text_lst, file="text.txt"):
        if type(text_lst) == list:
            with open(file, "w", encoding="utf-8") as f:
                for line in text_lst:
                    f.writelines(line + "\n")
        if type(text_lst) == str:
            with open(file, "w", encoding="utf-8") as f:
                f.writelines(text_lst)
        return file

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
        # self.matplot(time_arr,speed_arr)
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

    def video2audio(self, file):
        ffmpeg = "ffmpeg"
        print(file, self.Audio)
        cmd = '''%s -y -i "%s" -acodec pcm_s16le "%s"''' % (ffmpeg, file, self.Audio)
        print(cmd)
        os.system(cmd)

    def audio_get(self):
        import random
        import librosa

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

    def video_concat(self, dir):
        ffmpeg = "ffmpeg"
        f_lst = []
        for file in self.save_filename_list:
            file = "file '{}'".format(os.path.split(file)[-1])
            f_lst.append(file)
        if self.randomClip:
            import random

            random.shuffle(f_lst)
        self.videoInfo = os.path.join(dir, "videoInfo.txt")
        self.delFilesList.append(self.videoInfo)
        self.writeF(f_lst, self.videoInfo)
        self.videoOutput = os.path.join(dir, self.name + "_output" + ".mp4")
        cmd = '''{} -y -f concat -safe 0 -i "{}" -i "{}" -vcodec copy \
        -filter_complex "[0:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo,volume=0.2[a0]; \
        [1:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo,volume=0.5[a1];\
         [a0][a1]amerge=inputs=2[aout]" -map 0:v  -map "[aout]" -shortest "{}"'''.format(
            ffmpeg, self.videoInfo, self.bgm, self.videoOutput
        )
        cmd = '''{} -y -f concat -safe 0 -i "{}" -i "{}" -vcodec copy -c:a copy -shortest "{}"'''.format(
            ffmpeg, self.videoInfo, self.bgm, self.videoOutput
        )
        print("cmd:", cmd)
        os.chdir(dir)
        os.system(cmd)
        print(f"out video path:{self.videoOutput}")

    def audio_auto_cut(self):
        # self.video2audio(self.Movie)
        self.audio_get()
        self.audioDigital(self.Movie)
        if self.save_filename_list:
            self.video_concat(self.videoPath)


