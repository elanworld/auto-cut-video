from progressbar import ProgressBar, widgets, Percentage, Timer, Bar, ETA


class Tools:
    def progress_bar(self, total):
        widgets = ["AutoCutMovie: ", Percentage(), Bar("#"), Timer(), " ", ETA()]
        bar = ProgressBar(widgets=widgets, maxval=total).start()
        return bar
