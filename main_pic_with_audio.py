from moviepy.editor import *
from moviepy.video.fx.speedx import speedx
import wave
import numpy as np
import re
from progressbar import *
from common import python_box

tool = python_box.PythonBox()

class FfmpegPlugin:
    def __init__(self):
        self.t = time.time()
        global ffmpeg
        ffmpeg = "/data/data/com.termux/files/usr/bin/ffmpeg"
        ffmpeg = "ffmpeg"

    def __del__(self):
        print(time.time() - self.t)

    def video2audio(self, dir):
        f_lst = tool.dir_list(dir, "mp4$")
        for file in f_lst:
            wav = re.sub("mp4", "", file) + "wav"
            print(file, wav)
            cmd = "%s -y -i '%s' '%s'" % (ffmpeg, file, wav)
            print(cmd)
            os.system(cmd)

    def audio_split(self):
        f_lst = tool.dir_list(dir, "mp3$")
        for file in f_lst:
            seconds = 0
            while 1:
                m, s = divmod(seconds, 60)
                h, m = divmod(m, 60)
                start = ("%01d:%02d:%02d" % (h, m, s))
                end = "0:0:07"
                seconds += 7
                print(file)
                mp4 = file
                mp4_split = re.sub(".mp3", "", file) + "_%d.pcm" % seconds
                cmd = "{ffmpeg} -y -ss {start} -t {end} -i {mp4} -acodec pcm_s16le -f s16le -ac 1 -ar 16000 {mp4_split}".format(
                    ffmpeg=ffmpeg, start=start, end=end, mp4_split=mp4_split, mp4=mp4)
                print(cmd)
                os.system(cmd)
                size = os.path.getsize(mp4_split)
                if size == 0:
                    break

    def video_split(self, file):  # faster than moviepy
        mp4 = file
        mp4_split = re.sub(".mp4", "", file) + "_split.mp4"
        start = "0:0:9"
        end = "0:4:49"
        print(file)
        cmd = '''{ffmpeg} -y -ss {start} -t {end} -i "{mp4}" -vcodec copy -acodec copy "{mp4_split}"'''.format(
            ffmpeg=ffmpeg, start=start, end=end, mp4_split=mp4_split, mp4=mp4)
        print(cmd)
        os.system(cmd)

    def video_splt(self, file):
        split_dir = os.path.split(file)[0] + "/split"
        if not os.path.exists(split_dir):
            os.mkdir(split_dir)
        mp4 = file
        i = 1
        while i < 35:
            mp4_split = split_dir + "/split_" + str(i) + ".mp4"
            cmd = '''{ffmpeg} -y -ss {start} -t {end} -i "{mp4}" -vcodec h264  -acodec copy "{mp4_split}"'''.format(
                ffmpeg=ffmpeg,
                start=str(i), end=str(5.0), mp4_split=mp4_split, mp4=mp4)  # video codec change to h264
            print(cmd)
            os.system(cmd)
            i += 5.0
        return split_dir

    def video_concat(self, dir):
        os.chdir(dir)
        f_lst = []
        for file in tool.dir_list(dir, "mp4"):
            file = "file '{}'".format(file)
            f_lst.append(file)
        videoInfo = dir + "/videoInfo.txt"
        tool.write_file(f_lst, videoInfo)
        cmd = '''{} -f concat -i {} -c copy {}output.mp4'''.format(ffmpeg, videoInfo, dir + "/")
        print(cmd)
        os.chdir(dir)
        os.system(cmd)
        os.remove(videoInfo)

    def detect(self, file):
        ffmpeg = "ffmpeg"
        start = 0
        i = 1

        mp4 = file
        while start < 10:
            mp4_split = os.path.split(file)[0] + "/dd/" + str(i) + ".mp4"
            cmd = '''{ffmpeg} -y -ss {start} -t {end} -i "{mp4}" -vcodec copy -acodec copy "{mp4_split}"'''.format(
                ffmpeg=ffmpeg, start=start, end="1.3465", mp4_split=mp4_split, mp4=mp4)
            print(cmd)
            os.system(cmd)
            i += 1
            start += 1.3465


class MovieLib(FfmpegPlugin):
    def __init__(self, dir):
        super().__init__()
        self.dir = dir
        self.last_dir = os.path.split(dir)[0]
        self.image = tool.dir_list(dir, "jpg")
        self.audio_lst = tool.dir_list(self.last_dir + "/bgm", "mp3")
        self.imageVideo = self.last_dir + "/pic2video.mp4"
        self.imageAudio = self.last_dir + "/pic2video.wav"
        self.videoSpeed = self.last_dir + "/picSpeed.mp4"
        self.temp_videos = []

    def ImageSequence(self):
        # 只支持相同尺寸图片合成视频
        clip = ImageSequenceClip("/home/android/Desktop/文档/", fps=10)
        clip.write_videofile("result.mp4")

    def movie_concat(self, dir):  # 合并后衔接处卡顿重复
        outPath = dir + "/concatVideo.mp4"
        f_lst = tool.dir_list(dir, "mp4")
        videoClips = []
        for file in f_lst:
            videoClip = VideoFileClip(file)
            videoClips.append(videoClip)
        videoClip = concatenate_videoclips(videoClips)
        videoClip.write_videofile(outPath)

    def getFiles(self, dir, filter):
        files = os.listdir(dir)
        files_lst = []
        for file in files:
            if re.search(filter, file):
                file = dir + "/" + file
                files_lst.append(file)
        return files_lst

    def audio_wav(self):
        AudioClips = []
        for au in self.audio_lst:
            AudioClip = AudioFileClip(au)
            AudioClips.append(AudioClip)
        AudioClip = concatenate_audioclips(AudioClips)
        AudioClip = AudioClip.set_duration(self.video_time)
        AudioClip.write_audiofile(self.imageAudio)

    def clip_speed_change(self, clip, speed, a, b):  # keep change's time
        b = a + (b - a) * speed
        # print("clip:",a,speed,clip.duration)
        if b <= clip.duration:
            transform = lambda c: speedx(c, speed)
            clip = clip.subfx(transform, a, b)
            return clip
        else:
            return clip

    def num_speed(self, numpy_arr, n):
        new_numpy_arr = np.array([])
        for speed in numpy_arr:
            if speed > 1:
                new_speed = 1 + (speed - 1) * n
            else:
                if n <= 1:
                    new_speed = (1 - (1 - speed) * n)
                if n > 1:
                    new_speed = speed / n
            new_numpy_arr = np.append(new_numpy_arr, new_speed)
        return new_numpy_arr

    def matplot(self, x_lst, y_lst):
        import matplotlib.pyplot as plt
        plt.plot(x_lst, y_lst)
        plt.show()

    def audioDigital(self, audio):
        f = wave.open(audio, 'rb')
        params = f.getparams()
        nchannels, sampwidth, framerate, nframes = params[:4]
        self.framerate = framerate
        strData = f.readframes(nframes)
        f.close()
        waveData = np.fromstring(strData, dtype=np.short)
        waveData.shape = -1, 2
        waveData = waveData.T
        waveData = waveData[0]
        audioTime = np.arange(0, nframes) * (1.0 / framerate)
        np.abs(waveData, out=waveData)
        return audioTime, waveData

    def audio_anlysis(self):
        audio_speed = 1
        sens = 1
        # 视频速度匹配音频节奏 适用视频为重复性图片或者平调速度
        import sys
        sys.setrecursionlimit(10000)
        video = VideoFileClip(self.imageVideo)
        self.video_time = video.duration
        self.audio_wav()
        audioTime, wavedata = self.audioDigital(self.imageAudio)

        time_arr = np.array([])
        speed_arr = np.array([])
        clip = VideoFileClip(self.imageVideo)  # initial clip
        audioclip = clip.audio
        # 获取关键帧
        f = 0
        while f <= len(audioTime) - 1:
            t = audioTime[f]
            speed = np.mean(wavedata[f:f + self.framerate])
            f += self.framerate
            time_arr = np.append(time_arr, t)
            speed_arr = np.append(speed_arr, speed)

        # 调整速度敏感度
        speed_arr = speed_arr / np.mean(speed_arr)
        speed_arr = self.num_speed(speed_arr, 1.0 * sens)  # 速度变化敏感度
        speed_arr = speed_arr / np.mean(speed_arr)
        speed_arr = speed_arr * 1.0 * audio_speed  # 速率
        # 处理视频
        widgets = ['change speed: ', Percentage(), Bar("#"), Timer(), ' ', ETA()]
        bar = ProgressBar(widgets=widgets, maxval=len(speed_arr)).start()
        bar_n = 1
        for speed in speed_arr:
            bar.update(bar_n)
            bar_n += 1
            index = np.argwhere(speed_arr == speed)
            t = time_arr[index[0]]
            clip = self.clip_speed_change(clip, speed, t, t + 1)  # deal with clip
            time_arr = np.append(time_arr, t)
        clip.audio = audioclip
        print(self.videoSpeed)
        clip.write_videofile(self.videoSpeed + ".mp4", audio=False)

        clip = VideoFileClip(self.videoSpeed + ".mp4")  # solve cant write audio
        dur = clip.duration
        audio = AudioFileClip(self.imageAudio).set_duration(dur)
        clip.audio = audio
        clip.write_videofile(self.videoSpeed)
        # destroy
        del audio
        del clip
        os.remove(self.videoSpeed + ".mp4")
        try:
            os.remove(self.imageAudio)
        except:
            pass
        bar.finish()

    def imageToclip(self):
        import psutil
        width = 1080 * 4 / 3  # 视频默认尺寸
        height = 1080
        duration = 0.25  # 持续时间
        fps = 1.0 / duration
        width_height = width / height
        fail_dir = self.last_dir + "/MoviepyFailed/"
        bgm = self.getFiles(self.last_dir, "mp3$")
        audioClips = []
        for m in bgm:
            audioClip = AudioFileClip(m)
            audioClips.append(audioClip)
        audioClip = concatenate_audioclips(audioClips)

        listOfFiles = self.image
        listOfFiles.sort()
        widgets = ['Progress: ', Percentage(), Bar('#'), ' ', ETA()]
        bar = ProgressBar(widgets=widgets, maxval=len(self.image)).start()
        videoStartTime = 0
        videoClips = []
        fail_pic = []
        bar_i = 0
        for imageFileName in listOfFiles:
            bar_i += 1
            try:
                # print ('内存使用：',psutil.Process(os.getpid()).memory_info().rss/1024/1024)
                # print(imageFileName)
                imageClip = ImageClip(imageFileName)
                videoClip = imageClip.set_duration(duration)
                videoClip = videoClip.set_start(videoStartTime)
                v_w, v_h = videoClip.size  # 视频长宽
                w_h = v_w / v_h
                if w_h <= width_height:  # 宽度尺寸偏小
                    videoClip = videoClip.resize(width=width)
                    v_w, v_h = videoClip.size
                    videoClip = videoClip.crop(x_center=v_w / 2, y_center=v_h / 2, width=width, height=height)
                if w_h > width_height:
                    videoClip = videoClip.resize(height=height)
                    v_w, v_h = videoClip.size
                    videoClip = videoClip.crop(x_center=v_w / 2, y_center=v_h / 2, width=width, height=height)
                v_w, v_h = videoClip.size  # 视频长宽
                w_h = v_w / v_h
                videoStartTime += duration
                # videoClips.append(videoClip)
                if 'video' not in locals().keys():
                    video = videoClip
                else:
                    video = concatenate_videoclips([video, videoClip])
                    if psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024 > 800:  # 内存不足，分步写入
                        i = 1
                        temp_video = self.last_dir + "/temp" + str(i) + ".mp4"
                        while 1:
                            if os.path.exists(temp_video):
                                i += 1
                                temp_video = self.last_dir + "/temp" + str(i) + ".mp4"
                            else:
                                self.temp_videos.append(temp_video)
                                break
                        video.write_videofile(temp_video, fps=fps)
                        del video
            except Exception as e:
                fail_pic.append(imageFileName)
                cmd = "cp {file} {dir}".format(file=imageFileName, dir=fail_dir)
                # os.system(cmd)
                print(e)
            bar.update(bar_i)
        if len(self.temp_videos) > 0:
            videos = []
            for temp_video in self.temp_videos:
                video = VideoFileClip(temp_video)
                videos.append(video)
            video = concatenate_videoclips(videos)
        bar.finish()
        # video = concatenate_videoclips(videoClips)
        # 设置音轨长度
        video_duration = video.duration
        audio_duration = audioClip.duration
        while audio_duration < video_duration:
            audioClip = concatenate_audioclips([audioClip, audioClip])
            audio_duration = audioClip.duration
        audioClip = audioClip.set_duration(video_duration)
        video.audio = audioClip
        print("fail_pic:", len(fail_pic))
        video.write_videofile(self.imageVideo, fps=fps)

        del video
        for temp in self.temp_videos:
            os.remove(temp)

    def main(self):
        """
        批量图片合成clip
        通过bgm识别播放节奏，生成新的clip
        :return:
        """
        self.imageToclip()
        self.audio_anlysis()


if __name__ == "__main__":
    #pic to video clip
    dir = r"F:\Alan\Videos\我的视频"
    lib= MovieLib(dir)
    lib.main()


