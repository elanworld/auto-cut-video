from progressbar import ProgressBar, Percentage, Timer, Bar, ETA


class Tools:
    def __init__(self):
        self.name = "Tools"

    def progress_bar(self, total):
        widget = ["AutoCutMovie: ", Percentage(), Bar("#"), Timer(), " ", ETA()]
        bar = ProgressBar(widgets=widget, maxval=total).start()
        return bar

