from compare_frame import CompareFrame
from cut_movie import CutMovie
import cut_movie


class CutMovie(CutMovie, CompareFrame):
    """run from main.py"""

    def test():
        pass


if __name__ == "__main__":
    dir = r"F:\Alan\Videos\我的视频\知乎\cut_video"
    cut_movie.main(dir)
