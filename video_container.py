import cv2
from compare_frame import CompareFrame
import os
import re
import subprocess
from ffmpeg_box import FFmpegBox

class CaptureContainer:
    def __init__(self, file):
        self.file = file
        # need to define
        self.saveByFFmpeg = True
        self.save_short = 15
        self.save_long = 35

        self.__prepare()

    def __prepare(self):
        self.writer = WriterContainer()
        self.compare = CompareFrame()
        self.ffmpeg = FFmpegBox()
        self.capture = cv2.VideoCapture(self.file)
        self.width = self.capture.get(int(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = self.capture.get(int(cv2.CAP_PROP_FRAME_HEIGHT))
        self.total = self.capture.get(cv2.CAP_PROP_FRAME_COUNT)
        self.rate = self.capture.get(cv2.CAP_PROP_FPS)
        self.size = (int(self.width), int(self.height))
        self.save_file_num = 0

    def short_cut(self):
        frames = []
        if self.capture.isOpened():
            start_frame = 0
            end_frame = self.total
            frame_num = start_frame

            success, frame = self.capture.read()
            while frame_num <= end_frame:
                currentImg = frame
                frames.append(frame)
                success, frame = self.capture.read()
                if not success:
                    frame_num += 1
                    continue
                frame_num += 1
                lastImg = frame
                isSimilar = self.compare.classify_pHash(currentImg, lastImg)
                duration = (frame_num - start_frame) / self.rate
                if not isSimilar and duration > self.save_short or duration > self.save_long:
                    self.__output_control(start_frame, frame_num, self.rate, frames, self.size)
                    start_frame = frame_num + 1
                    frames.clear()
            self.capture.release()

    def __output_control(self, start_frame, frame_num, rate=24, frames=[], size=(1280, 720)):
        if self.saveByFFmpeg:
            start = start_frame / self.rate
            end = frame_num / self.rate
            self.ffmpeg.clip(self.file,
                            self.__get_outpath(self.file),
                             start,
                             end)
        else:
            save_first = self.__get_outpath(self.file)
            self.writer.save_video(save_first, frames, self.rate, self.size)
            self.ffmpeg.mix(self.__get_outpath(self.file), self.__random_bgm(), out_video)
            os.remove(save_first)

    def __get_outpath(self, file):
        self.save_file_num += 1
        dir = os.path.dirname(file)
        basename = os.path.basename(file)
        ext = os.path.splitext(file)[-1]
        name = re.sub(ext, '', basename)
        save_dir = os.path.join(dir, "out_py", name)
        if not os.path.exists(save_dir) and self.save_file_num == 1:
            os.makedirs(save_dir)
        save_file = os.path.join(save_dir, name + str(self.save_file_num) + ext)
        return save_file

    def __random_bgm(self):
        import random
        dir = r"F:\Alan\Music\AutoCutBGM\out"
        file_list = [os.path.join(dir, file) for file in os.listdir(dir)]
        random.shuffle(file_list)
        return file_list[0]


class WriterContainer:
    def save_video(self, file, frames, rate, size):
        writer = cv2.VideoWriter()
        writer.open(
            file, int(1145656920), rate, size, True
        )  # 参数2为avi格式的forucc，使用别的格式会导致转换出错
        for frame in frames:
            writer.write(frame)
        return True


