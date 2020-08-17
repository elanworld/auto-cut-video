from audio_box import AudioBox
import numpy as np
import os


class SpeechRecognize:
    def __init__(self, audio):
        self.audio = audio
        self.audio_box = AudioBox()
        self.y, self.time_data = self.audio_box.audio2dataByRosa(audio)
        self.rate = self.audio_box.framerate

        # need define
        self.__paint_audio = True
        self.speech_height = 0.2
        self.smallest_split = 0.5

    def paint(self):
        self.audio_box.matplot(self.y)

    def sharp(self):
        self.y = abs(self.y)
        self.y = self.audio_box.avg_data(self.y, int(self.rate * self.smallest_split))
        self.y = self.audio_box.balance(self.y)
        self.time = self.audio_box.get_time(self.y, self.time_data[-1])

    def recognize(self):
        self.sharp()
        if self.__paint_audio:
            self.paint()
        clip_index = self.audio_box.clip_data(self.y, self.speech_height)
        clips_time = []
        for clip in clip_index:
            clips_time.append([self.time[clip[0]], self.time[clip[1]]])
        from util import Tools
        from ffmpeg_box import FFmpegBox
        ffmpeg = FFmpegBox()
        tools = Tools()
        outfiles = []
        for clip in clips_time:
            outfile = tools.get_outpath(self.audio)
            outfiles.append(outfile)
            ffmpeg.clip(self.audio, outfile, clip[0], clip[1])
        dir, name, ext = tools.split_path(self.audio)
        ffmpeg.join(outfiles, os.path.join(dir, name + "_speech" + ext))


if __name__ == '__main__':
    file = r"F:\Alan\Videos\电影\audio_read.wav"
    box = SpeechRecognize(file)
    box.recognize()
