from progressbar import ProgressBar, widgets, Percentage, Timer, Bar, ETA
import os
import re


class Tools:
    def __init__(self):
        self.__outpath_num = 0

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

    def get_outpath(self, file):
        self.__outpath_num += 1
        dir, name, ext = self.split_path(file)
        save_dir = os.path.join(dir, "out_py", name)
        if not os.path.exists(save_dir) and self.__outpath_num == 1:
            os.makedirs(save_dir)
        save_file = os.path.join(save_dir, name + str(self.__outpath_num) + ext)
        return save_file

    def split_path(self, file):
        basename = os.path.basename(file)
        dir = os.path.dirname(file)
        ext = os.path.splitext(file)[-1]
        name = re.sub(ext, '', basename)
        return dir, name, ext
