from progressbar import ProgressBar, widgets, Percentage, Timer, Bar, ETA


class Tools:
    def progress_bar(self, total):
        widgets = ["AutoCutMovie: ", Percentage(), Bar("#"), Timer(), " ", ETA()]
        bar = ProgressBar(widgets=widgets, maxval=total).start()
        return bar

    def writeF(self, text_lst, file="text.txt"):
        if type(text_lst) == list:
            with open(file, "w", encoding="utf-8") as f:
                for line in text_lst:
                    f.writelines(line + "\n")
        if type(text_lst) == str:
            with open(file, "w", encoding="utf-8") as f:
                f.writelines(text_lst)
        return file
