import os
import sys
import re
import random
import subprocess
import time
import cv2
import numpy as np


class CutMovie():
    '''Auto cut video'''

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

    def video2audio(self, file):
        ffmpeg = "ffmpeg"
        print(file, self.Audio)
        cmd = '''%s -y -i "%s" -acodec pcm_s16le "%s"''' % (ffmpeg, file, self.Audio)
        print(cmd)
        os.system(cmd)

    def video_concat(self, dir):
        ffmpeg = "ffmpeg"
        f_lst = []
        for file in self.save_filename_list:
            file = "file '{}'".format(os.path.split(file)[-1])
            f_lst.append(file)
        if self.randomClip:
            random.shuffle(f_lst)
        self.videoInfo = os.path.join(dir, "videoInfo.txt")
        self.delFilesList.append(self.videoInfo)
        self.writeF(f_lst, self.videoInfo)
        self.videoOutput = os.path.join(dir, self.name + "_output" + ".mp4")
        cmd = '''{} -y -f concat -safe 0 -i "{}" -i "{}" -vcodec copy -c:a copy -shortest "{}"'''.format(
            ffmpeg, self.videoInfo, self.bgm, self.videoOutput
        )
        print("cmd:", cmd)
        os.chdir(dir)
        os.system(cmd)
        print(f"out video path:{self.videoOutput}")
