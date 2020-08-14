from utils import Tools
from video_container import CaptureContainer
import sys


class MainShortCut(CaptureContainer):
    def __init__(self, file, **kwargs):
        super().__init__(file, **kwargs)
        if len(sys.argv) >= 2:
            self.file = sys.argv[1]

        # need to define
        self.saveByFFmpeg = True
        self.save_short = 15
        self.save_long = 35

        self.short_cut()


if __name__ == '__main__':
    file = r"F:\Alan\Videos\Mine\PERFECT FLASH.mp4"
    MainShortCut(file)
