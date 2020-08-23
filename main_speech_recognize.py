from audio_box import AudioBox
import os
from common.python_box import FileSys
from ffmpeg_box import FFmpegBox


class SpeechRecognize:
    def __init__(self, file):
        self.audio_box = AudioBox()
        self.ffmpeg = FFmpegBox()
        self.tools = FileSys()

        self.file = file
        self.y, self.time = self.audio_box.audio2data_rosa(self.file)
        self.rate = self.audio_box.framerate

        # need define
        self.__paint_audio = True
        self.speech_height = 0.1
        self.smallest_split = 0.01

    def __paint(self):
        self.audio_box.matplot(self.y, self.time)

    def __sharp(self):
        self.y = abs(self.y)
        self.y = self.audio_box.avg_data(self.y, int(self.rate * self.smallest_split))
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
        audio_format = ["mp3","wav","m4a"]
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

    def recognize(self):
        self.__sharp()
        if self.__paint_audio:
            self.__paint()
        time_clips = self.__get_clips()
        files = self.__cut_clips(time_clips)
        dir, name, ext = self.tools.split_path(self.file)
        out_file = os.path.join(dir, name + "_speech" + ext)
        self.ffmpeg.concat(files,out_file)

if __name__ == '__main__':
    file = r"G:\Alan\Documents\录音\java基础.m4a"
    box = SpeechRecognize(file)
    box.recognize()
