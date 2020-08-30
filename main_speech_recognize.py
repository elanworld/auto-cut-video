import os
import sys

parent = os.path.split(os.getcwd())[0]
sys.path.append(parent)

from common.python_box import FileSys
from ffmpeg_box import FFmpegBox
from audio_box import AudioBox


class SpeechRecognize:
    def __init__(self, file):
        self.audio_box = AudioBox()
        self.ffmpeg = FFmpegBox()
        self.tools = FileSys()

        self.file = file
        self.y, self.time = self.audio_box.audio2data_rosa(self.file)
        self.rate = self.audio_box.framerate

        # need define
        self.__paint_audio = False
        self.speech_height = 0.1
        self.smallest_split = 0.01

        self._prepare()

    def __del__(self):
        for f in self.clean_file:
            if os.path.exists(f):
                os.remove(f)

    def _prepare(self):
        self.clean_file = []
        parent, name, ext = self.tools.split_path(self.file)
        if ext in [".mp4"]:
            self.is_video = True
        else:
            self.is_video = False
        self.out_file = os.path.join(parent, name + "_speech" + ext)
        self.temp = os.path.join(parent, name + "_temp" + ext)

    def __paint(self):
        self.audio_box.matplot(self.y, self.time)

    def __sharp(self):
        self.y = abs(self.y)
        self.y = self.audio_box.avg_data(self.y, int(self.rate * self.smallest_split))
        self.y = self.audio_box.balance(self.y)
        self.y = self.audio_box.optimiza_data(self.y)
        self.y = self.audio_box.balance(self.y)
        self.time = self.audio_box.time_get(self.y, self.time[-1])

    def __get_clips(self):
        clip_index = self.audio_box.clip_data(self.y, self.speech_height)
        time_clips = []
        for clip in clip_index:
            time_clips.append([self.time[clip[0]], self.time[clip[1]]])
        new_time_clips = self.audio_box.time_edge_processs(time_clips)
        return new_time_clips

    def concat_video(self, files, outfile):
        from moviepy import editor
        audio_format = ["mp3", "wav", "m4a"]
        is_audio = False
        for format in audio_format:
            if format in files[0]:
                is_audio = True
        clips = []
        if is_audio:
            for file in files:
                clip = editor.AudioFileClip(file)
                clips.append(clip)
            audioclips = editor.concatenate_audioclips(clips)
            audioclips.write_audiofile(outfile)
        else:
            for file in files:
                clip = editor.VideoFileClip(file)
                clips.append(clip)
            videoclips = editor.concatenate_videoclips(clips)
            videoclips.write_videofile(outfile)

    def __cut_clips(self, time_clips):
        files = []
        for clip in time_clips:
            outpath = self.tools.get_outpath(self.file)
            if not os.path.exists(outpath):
                self.ffmpeg.clip(self.file, outpath, clip[0], clip[1])
                if not os.path.exists(outpath):
                    continue
            files.append(outpath)
        return files

    def _get_clips_silence(self, time_clips: list):
        time_clips_silence = []
        for i in range((len(time_clips) - 1)):
            print(time_clips[i], time_clips[i + 1])
            last = time_clips[i][1]
            current = time_clips[i + 1][0]
            time_clips_silence.append([last, current])
        return time_clips_silence

    def _denoising(self, time_clips: list):
        silence = self._get_clips_silence(time_clips)
        outwav = "out_file.wav"
        noise = "noise.wav"
        config = "noise.prof"
        outwav_clean = "out_clean.wav"
        for file in [outwav, noise, config, outwav_clean, self.temp]:
            self.clean_file.append(file)
        self.ffmpeg.set_input(self.file).set_fiter_select(time_clips, False).set_output(outwav).run()
        self.ffmpeg.set_fiter_select(silence, False).set_output(noise).run()
        cmd = f"sox {noise} -n noiseprof {config}"
        print(cmd)
        os.system(cmd)
        cmd = f"sox {outwav} {outwav_clean} noisered noise.prof 0.21"
        print(cmd)
        os.system(cmd)
        if self.is_video:
            self.ffmpeg.set_input(self.file).set_fiter_select(time_clips).set_output(self.temp).run()
            self.ffmpeg.clear().set_input_mul([self.temp, outwav_clean]). \
                set_output(self.out_file).set_map("-map 0:v -map 1:a").run()
        else:
            self.ffmpeg.set_input(outwav_clean).set_output(self.out_file).run()

    def get_time_clips(self):
        self.__sharp()
        if self.__paint_audio:
            self.__paint()
        time_clips = self.__get_clips()
        return time_clips

    def run(self):
        self.__sharp()
        if self.__paint_audio:
            self.__paint()
        time_clips = self.__get_clips()
        self._denoising(time_clips)


if __name__ == '__main__':
    file = input("请输入路径:")
    box = SpeechRecognize(file)
    box.run()
