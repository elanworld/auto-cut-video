from compare_frame import CompareFrame
from cut_movie import CutMovie
from audio_voice import AudioVoice
from utils import Tools
import sys


class MainCutVideo(CutMovie, CompareFrame, AudioVoice, Tools):
    """run from Main.py"""

    def __init__(self, file):
        super().__init__(file)
        if len(sys.argv) >= 3:
            self.bgmPath = sys.argv[2]
            print("BGM path:", sys.argv[2])


def test(file):
    cut = MainCutVideo(file)
    cut.audio_auto_cut()


def main(dir, video_format="mp4"):
    if len(sys.argv) >= 3:
        print("Video path:", sys.argv[1])
        dir = sys.argv[1]
    for file in os.listdir(dir):
        if re.search(video_format, file):
            file = os.path.join(dir, file)
            print("cutting video:", file)
            cut = MainCutVideo(file)
            cut.audio_auto_cut()
    print("auto cut all video done!")


if __name__ == "__main__":
    file = r"F:\Alan\Videos\我的视频\剪辑\zedd-beautiful.mp4"
    test(file)
