from progressbar import ProgressBar, widgets, Percentage, Timer, Bar, ETA
import os
import re


class Tools:
    def __init__(self):
        self.name = "Tools"

    def progress_bar(self, total):
        widgets = ["AutoCutMovie: ", Percentage(), Bar("#"), Timer(), " ", ETA()]
        bar = ProgressBar(widgets=widgets, maxval=total).start()
        return bar

