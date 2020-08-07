import cv2
from compare_frame import CompareFrame
import os
import re
import subprocess


class CaptureContainer:
    def __init__(self, file, **kwargs):
        self.file = file
        self.capture = cv2.VideoCapture(file)
        self.width = self.capture.get(int(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = self.capture.get(int(cv2.CAP_PROP_FRAME_HEIGHT))
        self.total = self.capture.get(cv2.CAP_PROP_FRAME_COUNT)
        self.rate = self.capture.get(cv2.CAP_PROP_FPS)
        self.size = (int(self.width), int(self.height))

        self.writer = WriterContainer()
        self.compare = CompareFrame()
        self.ffmpeg = FFmpeg()

        dir, name, ext = self.get_path(file)
        self.save_dir = os.path.join(dir, name)
        self.mkdir(self.save_dir)
        self.save_file = os.path.join(self.save_dir, name + '_')

        # need to define
        self.saveByFFmpeg = True
        self.start = 10
        self.end = self.total / self.rate - 10

        self.save_file_num = 0
        self.strar_frame = 0
        self.end_frame = self.total

    def short_cut(self):
        frames = []
        if self.capture.isOpened():
            self.capture.set(cv2.CAP_PROP_POS_FRAMES, self.strar_frame)
            start_frame = self.strar_frame
            end_frame = self.end_frame

            frame_num = int(start_frame)
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
                isSimilar = self.compare.classify_pHash(currentImg, lastImg, boundary=19)
                duration = (frame_num - start_frame) / self.rate
                if not isSimilar and duration > 12 or duration > 40:
                    self.output_control(start_frame, frame_num, self.rate,frames,self.size)
                    start_frame = frame_num + 1
                    frames.clear()
            self.capture.release()

    def output_control(self, start_frame, frame_num, rate=24,frames=[],size=(1280, 720)):
        self.save_file_num += 1
        out_file = self.save_file + str(self.save_file_num) + ".mp4"
        print(out_file)
        if self.saveByFFmpeg:
            self.ffmpeg.cut_size(self.file,
                            out_file,
                            start_frame,
                            frame_num,
                            self.rate)
        else:
            self.writer.save_video(out_file, frames, self.rate, self.size)
            out_video = self.save_file + str(self.save_file_num) + "_audio.mp4"
            self.ffmpeg.conbine(out_file, self.random_bgm(), out_video)
            os.remove(out_file)


    def mkdir(self, path):
        if not os.path.exists(path):
            os.mkdir(path)

    def get_path(self, file):
        dir = os.path.dirname(file)
        basename = os.path.basename(file)
        ext = os.path.splitext(file)[-1]
        name = re.sub(ext, '', basename)
        return dir, name, ext

    def random_bgm(self):
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


class FFmpeg:
    def cut(self, filename, save_filename, startFrame=0, stopFrame=1, rate=24):
        cmd = f'ffmpeg -y -ss {str(startFrame / rate)} -to {str(stopFrame / rate)} -i "{filename}" -c copy "{save_filename}"'
        os.system(cmd)
        print(cmd)

    #todo 规范化接口 参数
    def cut_size(self, filename, save_filename, startFrame=0, stopFrame=1, rate=24):
        filt = f"-vf crop=600:720:{(1280-600)/2}:0"
        cmd = f'ffmpeg -y -ss {str(startFrame / rate)} -to {str(stopFrame / rate)} -i "{filename}" {filt} "{save_filename}"'
        os.system(cmd)
        print(cmd)

    def conbine(self, video, audio, out_file):
        cmd = f'ffmpeg -y -i "{video}" -i "{audio}" -c copy -shortest "{out_file}"'
        os.system(cmd)
        print(cmd)


if __name__ == '__main__':
    file = r"F:\Alan\Videos\我的视频\selenium_download\Most Awesome Zach King Magic Tricks - New Zach King Magic 2019.mp4"
    container = CaptureContainer(file)
    container.short_cut()
