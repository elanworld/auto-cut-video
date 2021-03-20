from typing import Tuple, Union, Any

from moviepy.editor import *
from moviepy.video.fx.speedx import speedx
import wave
import numpy as np
import re
from progressbar import *
import python_box
import psutil
import time

file_sys = python_box.FileSys()


class FfmpegPlugin:
    def __init__(self):
        self.t = time.time()
        self.ffmpeg = "ffmpeg"

    def __del__(self):
        print("use time:", time.time() - self.t)

    def video2audio(self, directory):
        f_lst = file_sys.dir_list(directory, "mp4$")
        for file in f_lst:
            wav = re.sub("mp4", "", file) + "wav"
            print(file, wav)
            cmd = "%s -y -i '%s' '%s'" % (self.ffmpeg, file, wav)
            print(cmd)
            os.system(cmd)

    def audio_split(self, directory):
        f_lst = file_sys.dir_list(directory, "mp3$")
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
                    ffmpeg=self.ffmpeg, start=start, end=end, mp4_split=mp4_split, mp4=mp4)
                print(cmd)
                os.system(cmd)
                size = os.path.getsize(mp4_split)
                if size == 0:
                    break

    def video_split(self, file):
        mp4 = file
        mp4_split = re.sub(".mp4", "", file) + "_split.mp4"
        start = "0:0:9"
        end = "0:4:49"
        print(file)
        cmd = '''{ffmpeg} -y -ss {start} -t {end} -i "{mp4}" -vcodec copy -acodec copy "{mp4_split}"'''.format(
            ffmpeg=self.ffmpeg, start=start, end=end, mp4_split=mp4_split, mp4=mp4)
        print(cmd)
        os.system(cmd)

    def video_concat(self, dir):
        os.chdir(dir)
        f_lst = []
        for file in file_sys.dir_list(dir, "mp4"):
            file = "file '{}'".format(file)
            f_lst.append(file)
        videoInfo = dir + "/videoInfo.txt"
        file_sys.write_file(f_lst, videoInfo)
        cmd = '''{} -f concat -i {} -c copy {}output.mp4'''.format(self.ffmpeg, videoInfo, dir + "/")
        print(cmd)
        os.chdir(dir)
        os.system(cmd)
        os.remove(videoInfo)


def imageSequence(directory, target):
    # 只支持相同尺寸图片合成视频
    clip = ImageSequenceClip(directory, fps=10)
    clip.write_videofile(target)


def movie_concat(directory):  # 合并后衔接处卡顿重复
    outPath = directory + "/concatVideo.mp4"
    f_lst = file_sys.dir_list(directory, "mp4")
    videoClips = []
    for file in f_lst:
        videoClip = VideoFileClip(file)
        videoClips.append(videoClip)
    videoClip = concatenate_videoclips(videoClips)
    videoClip.write_videofile(outPath)


def clip_speed_change(clip, speed, ta, tb):
    """
    调节速度
    keep change's time
    :param clip:
    :param speed:
    :param ta: 开始时间
    :param tb: 结束时间
    :return:
    """
    tb = ta + (tb - ta) * speed
    if tb <= clip.duration:
        speed_lambda = lambda c: speedx(c, speed)
        try:
            clip = clip.subfx(speed_lambda, ta, tb)
            # 此处报错关闭所有python即可解决,升级库
        except Exception as e:
            print(e)
    return clip


def num_speed(numpy_arr, n):
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


def get_current_index(np_array: np.ndarray, value):
    """
    获取顺序排序数组中t附近的索引
    :param np_array:
    :param value:
    :return:
    """
    index = np.where(np_array <= value)
    if len(index) > 0:
        if len(index[0]) > 0:
            return index[0][len(index[0]) - 1]
    return len(np_array) - 1


class MovieLib(FfmpegPlugin):
    def __init__(self, dir):
        super().__init__()
        self.dir = dir
        self.last_dir = os.path.split(dir)[0]
        self.image_list = file_sys.dir_list(dir, "jpg")
        self.audio_lst = file_sys.dir_list(os.path.join(self.last_dir, "bgm"))
        self.imageVideo = os.path.join(self.last_dir, "pic2video.mp4")
        self.audio_file = os.path.join(self.last_dir, "pic2video.wav")
        self.speed_video_file = os.path.join(self.last_dir, "picSpeed.mp4")
        self.temp_videos = []
        # 速度变化敏感度
        self.sens = 1.2
        self.change_speed_time = 0.8
        self.audio_leader = True

    def audio2data(self, audio):
        f = wave.open(audio, 'rb')
        params = f.getparams()
        nchannels, sampwidth, self.framerate, nframes = params[:4]
        strData = f.readframes(nframes)
        f.close()
        waveData = np.fromstring(strData, dtype=np.short)
        waveData.shape = -1, 2
        waveData = waveData.T
        waveData = waveData[0]
        audioTime = np.arange(0, nframes) * (1.0 / self.framerate)
        np.abs(waveData, out=waveData)
        return audioTime, waveData

    def frame2speed(self, audioTime: list, wave_data: list, f_duration=None) -> Tuple[
        np.ndarray, Union[Union[float, int], Any]]:
        """
        根据帧获取音频速度
        :param f_duration:
        :param audioTime:
        :param wave_data:
        :return:
        """
        np_time = np.array([])
        np_speed = np.array([])
        # 获取关键帧
        f = 0
        if f_duration is None:
            f_duration = int(self.framerate * 0.2)
        while f <= len(audioTime) - 1:
            t = audioTime[f]
            speed = np.mean(wave_data[f:f + f_duration])
            f += f_duration
            np_time = np.append(np_time, t)
            np_speed = np.append(np_speed, speed)
        # 调整速度敏感度
        np_speed = np_speed / np.mean(np_speed)
        np_speed = np.where(np_speed >= 8, 8, np_speed)
        np_speed = np.where(np_speed <= 0.2, 0.2, np_speed)
        np_speed = np.where(np_speed >= 1, np_speed * self.sens, np_speed)
        np_speed = np.where(np_speed < 1, np_speed / self.sens, np_speed)
        np_speed = np_speed / np.mean(np_speed)
        return np_time, np_speed

    def video_speed_with_audio(self):
        # 视频速度匹配音频节奏 适用视频为重复性图片或者平调速度
        sys.setrecursionlimit(10000000)
        video = VideoFileClip(self.imageVideo)
        video.audio.write_audiofile(self.audio_file)
        audioTime, wave_data = self.audio2data(self.audio_file)
        np_time, np_speed = self.frame2speed(audioTime, wave_data,
                                             f_duration=int(self.framerate * self.change_speed_time))
        # 处理视频
        bar_setting = ['change speed: ', Percentage(), Bar("#"), Timer(), ' ', ETA()]
        speed_clip = VideoFileClip(self.imageVideo)  # initial clip
        audio_clip = speed_clip.audio
        bar = ProgressBar(widgets=bar_setting, maxval=len(np_speed)).start()
        bar_update_tie = 1
        for i in range(len(np_speed)):
            bar.update(bar_update_tie)
            bar_update_tie += 1
            speed = np_speed[i]
            t = np_time[i]
            speed_clip = clip_speed_change(speed_clip, speed, t, t + self.change_speed_time)  # 分段变速
            np_time = np.append(np_time, t)
        speed_clip.audio = audio_clip
        print(self.speed_video_file)
        video_without_audio = file_sys.get_outfile(self.speed_video_file, "no_audio")
        speed_clip.write_videofile(video_without_audio, audio=False)

        speed_clip = VideoFileClip(video_without_audio)  # solve cant write audio
        duration = speed_clip.duration
        audio = AudioFileClip(self.audio_file)
        audio.set_duration(duration)
        speed_clip.audio = audio
        speed_clip.write_videofile(self.speed_video_file)
        # destroy
        del audio
        del speed_clip
        try:
            os.remove(video_without_audio)
            os.remove(self.audio_file)
            os.remove(self.imageVideo)
        except Exception as e:
            print(e)
        bar.finish()

    def compute_time_line(self, np_time: np.ndarray, np_speed: np.ndarray, clips: list, audio_duration) -> list:
        """
        算法循环找出clip适合的时长，使总时长接近audio_duration
        :param np_time:
        :param np_speed:
        :param clips:
        :param audio_duration:
        :return:
        """
        plus = None
        reduce = None
        default_var = audio_duration / len(clips)
        durations = []
        while True:
            durations.clear()
            for _ in clips:
                index = get_current_index(np_time, sum(durations))
                duration = 1.0 / np_speed[index]
                clip_duration = duration * default_var
                durations.append(clip_duration)
            total = sum(durations)
            if total > audio_duration:
                default_var *= 0.99
                reduce = True
            if total <= audio_duration:
                default_var *= 1.01
                plus = True
            if plus and reduce:
                break
        return durations

    def crop_clip(self, clip: ImageClip, width=1080 * 4 / 3, height=1080):
        w, h = clip.size  # 视频长宽
        w_h = w / h
        if w_h <= width / height:  # 宽度尺寸偏小
            clip = clip.resize(width=width)
            w, h = clip.size
            clip = clip.crop(x_center=w / 2, y_center=h / 2, width=width, height=height)
        if w_h > width / height:
            clip = clip.resize(height=height)
            w, h = clip.size
            clip = clip.crop(x_center=w / 2, y_center=h / 2, width=width, height=height)
        return clip

    def image2speed_video(self, width=1080 * 4 / 3, height=1080):
        """
        图片直接生成变速视频
        跳过图片生成视频步骤
        :param width:
        :param height:
        :return:
        """
        # 生成音频数据
        if len(self.audio_lst) == 0:
            raise Exception("exists any music")
        audio_clips = []
        for m in self.audio_lst:
            clip = AudioFileClip(m)
            audio_clips.append(clip)
        audio_clip = concatenate_audioclips(audio_clips)
        audio_clip.write_audiofile(self.audio_file)
        audioTime, wave_data = self.audio2data(self.audio_file)
        np_time, np_speed = self.frame2speed(audioTime, wave_data)
        time_line = self.compute_time_line(np_time, np_speed, self.image_list, audio_clip.duration)

        self.image_list.sort()
        image_clips = []
        for i in range(len(self.image_list)):
            image_clip = ImageClip(self.image_list[i])
            image_clip.start = sum(time_line[0:i])
            image_clip.duration = time_line[i]
            image_clip.fps = 1
            image_clip = self.crop_clip(image_clip, width, height)
            image_clips.append(image_clip)

        video_clip = concatenate_videoclips(image_clips)
        video_clip.audio = audio_clip
        video_clip.write_videofile(self.speed_video_file, fps=(int(1 / min(time_line)) + 1))
        os.remove(self.audio_file)

    def image2clip(self, width=1080 * 4 / 3, height=1080, duration=0.25):
        fps = 1.0 / duration
        width_height = width / height
        if len(self.audio_lst) == 0:
            raise Exception("exists any music")
        audioClips = []
        for m in self.audio_lst:
            audioClip = AudioFileClip(m)
            audioClips.append(audioClip)
        audioClip = concatenate_audioclips(audioClips)

        self.image.sort()
        bar_setting = ['image2clip: ', Percentage(), Bar('#'), ' ', ETA()]
        bar = ProgressBar(widgets=bar_setting, maxval=len(self.image)).start()
        videoStartTime = 0
        videoClips = []
        fail_pic = []
        bar_i = 0
        for imageFileName in self.image:
            bar_i += 1
            try:
                imageClip = ImageClip(imageFileName)
                videoClip = imageClip.set_duration(duration)
                videoClip = videoClip.set_start(videoStartTime)
                videoClip = self.crop_clip(videoClip, width, height)
                videoStartTime += duration
                if 'video_clip' not in locals().keys():
                    video_clip = videoClip
                else:
                    video_clip = concatenate_videoclips([video_clip, videoClip])
                    # 内存不足时，分步写入
                    if psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024 > 800:
                        i = 1
                        temp_video = file_sys.get_outfile(self.imageVideo, str(i))
                        while 1:
                            if os.path.exists(temp_video):
                                i += 1
                                temp_video = file_sys.get_outfile(self.imageVideo, str(i))
                            else:
                                self.temp_videos.append(temp_video)
                                break
                        video_clip.write_videofile(temp_video, fps=fps)
                        del video_clip
            except Exception as e:
                fail_pic.append(imageFileName)
                print(e)
            bar.update(bar_i)
        if len(self.temp_videos) > 0:
            videos = []
            for temp_video in self.temp_videos:
                video_clip = VideoFileClip(temp_video)
                videos.append(video_clip)
            video_clip = concatenate_videoclips(videos)
        bar.finish()
        # 设置音轨长度
        video_duration = video_clip.duration
        audio_duration = audioClip.duration
        if self.audio_leader:
            video_clip = video_clip.subfx(lambda c: speedx(c, video_duration / audio_duration))
        else:
            while audioClip.duration < video_duration:
                audioClip = concatenate_audioclips([audioClip, audioClip])
            audioClip = audioClip.set_duration(video_duration)
        video_clip.audio = audioClip
        video_clip.write_videofile(self.imageVideo, fps=fps)
        del video_clip
        for temp in self.temp_videos:
            try:
                os.remove(temp)
            except Exception as e:
                print(e)
        return self.imageVideo

    def run(self):
        """
        批量图片合成clip
        通过bgm识别播放节奏，生成新的clip
        :return:
        """
        self.image2speed_video()


if __name__ == "__main__":
    """
    pic to video clip
    """
    directory = python_box.get_agv()
    n = MovieLib(directory)
    n.run()
