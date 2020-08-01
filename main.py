from compare_frame import CompareFrame
from cut_movie import CutMovie
from audio_voice import AudioVoice
from tools import Tools


class CutMovie(CutMovie, CompareFrame, AudioVoice, Tools):
    """run from Main.py"""


def test(file):
    cut = CutMovie(file)
    cut.audio_auto_cut()

def main(dir, video_format="mp4"):
    if len(sys.argv) >= 3:
        print("Video path:", sys.argv[1])
        dir = sys.argv[1]
    for file in os.listdir(dir):
        if re.search(video_format, file):
            file = os.path.join(dir, file)
            print("cutting video:", file)
            cut = CutMovie(file)
            cut.audio_auto_cut()
    print("auto cut all video done!")

if __name__ == "__main__":
    file = r"F:\Alan\Videos\我的视频\知乎\BBC.Planet.Earth.II.4行星地球精彩片段_Trim.mp4"
    test(file)
