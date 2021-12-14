import os
import re

from compare_frame import CompareFrame
from cut_movie import CutMovie
from audio_voice import AudioVoice
from util import Tools
import sys
import audio_voice


class MainCutVideo(CutMovie, CompareFrame, AudioVoice, Tools):
    """run from Main.py"""

    def __init__(self, file):
        super().__init__(file)
        if len(sys.argv) >= 3:
            self.bgmPath = sys.argv[2]
            print("BGM path:", sys.argv[2])

    def main(self, directory, video_format="mp4"):
        if len(sys.argv) >= 3:
            print("Video path:", sys.argv[1])
            directory = sys.argv[1]
            print("BGM path:", sys.argv[2])
            self.bgmPath = sys.argv[2]
        for file in os.listdir(directory):
            if re.search(video_format, file):
                file = os.path.join(directory, file)
                print("cutting video:", file)
                cut = MainCutVideo(file)
                cut.audio_auto_cut()
        print("auto cut all video done!")


def test(file):
    cut = MainCutVideo(file)
    cut.audio_auto_cut()


if __name__ == "__main__":
    wav = r"F:\Alan\Videos\电影\audio_read.wav"
    voice = audio_voice.AudioVoice(wav)
    voice.audio2dataByRosa(wav)
