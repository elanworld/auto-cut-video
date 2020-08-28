import os
import collections
from common import python_box


class FFmpegBox:
    def __init__(self):
        self.ffmpeg = "ffmpeg"
        self.file_sys = python_box.FileSys()

        self._prepare()

    def _prepare(self):
        self.cmd_dic = collections.OrderedDict()
        self.cmd_dic["ffmpeg"] = self.ffmpeg
        self.cmd_dic["over_write"] = "-y"
        self.cmd_dic["input"] = None
        self.cmd_dic["clipper"] = None
        self.cmd_dic["filter_complex"] = None
        self.cmd_dic["map"] = None
        self.cmd_dic["codec"] = None
        self.cmd_dic["output"] = None

    def run(self):
        cmds = []
        for cmd in self.cmd_dic.values():
            if cmd:
                cmds.append(cmd)
        cmd_line = " ".join(cmds)
        print(cmd_line)
        os.system(cmd_line)

    def clear(self):
        self._prepare()
        return self

    def set_input(self, file):
        self.cmd_dic["input"] = "-i \"" + file + "\""
        return self

    def set_input_mul(self, file_list: list):
        if len(file_list) == 0:
            raise Exception("None input file")
        if len(file_list) == 1:
            self.set_input(file_list[0])
        for i in range(len(file_list)):
            file_list[i] = f"\"{file_list[i]}\""
        files = '-i ' + " -i ".join(file_list)
        self.cmd_dic["input"] = files
        return self

    def set_output(self, file):
        self.cmd_dic["output"] = "\"" + file + "\""
        return self

    def set_map(self, map: str):
        self.cmd_dic["map"] = map
        return self

    def set_fiter_select(self, time_list: list, video=True):
        trims_join = "-filter_complex "
        selects = []
        size = len(time_list)
        for i in range(size):
            select = f"between(t,{round(time_list[i][0], 3)},{round(time_list[i][1], 3)})"
            selects.append(select)
        selects = "+".join(selects)
        if video:
            trims_join += "select='" + selects + "',setpts=N/FRAME_RATE/TB;aselect='" + selects + "',asetpts=N/SR/TB"
        else:
            trims_join += "aselect='" + selects + "',asetpts=N/SR/TB"
        self.cmd_dic["filter_complex"] = trims_join
        return self

    def clip(self, filename, save_filename, start, stop):
        cmd = f'ffmpeg -y -i "{filename}" -ss {str(start)} -to {str(stop)} "{save_filename}"'
        print(cmd)
        os.system(cmd)

    def crop(self, filename, save_filename, start, stop):
        filt = f"-vf crop=600:720:{(1280 - 600) / 2}:0"
        cmd = f'ffmpeg -y -i "{filename}" -ss {str(start)} -to {str(stop)} {filt} "{save_filename}"'
        print(cmd)
        os.system(cmd)

    def mix(self, video, audio, out_file):
        cmd = f'ffmpeg -y -i "{video}" -i "{audio}" -c copy -shortest "{out_file}"'
        print(cmd)
        os.system(cmd)

    def join(self, file_lst, out_file):
        jion_file = "-i " + " -i ".join(file_lst)
        cmd = f"ffmpeg -y {jion_file} -filter_complex concat=n={len(file_lst)}:v=1:a=1[outv][outa] -map [outv] -map [outa] {out_file}"
        print(cmd)
        os.system(cmd)

    def trim(self, file, outfile, time_list: list):
        """
        concat multiple clip from nultiple times in one file
        :param file:
        :param time_list:
        :return:
        """
        vtrims = []
        atrims = []
        concat_vas = []
        size = len(time_list)
        for i in range(size):
            vtrim = f"[0:v]trim={time_list[i][0]}:{time_list[i][1]}[v{i}]"
            atrim = f"[0]atrim={time_list[i][0]}:{time_list[i][1]}[a{i}]"
            concat_va = f"[v{i}][a{i}]"
            vtrims.append(vtrim)
            atrims.append(atrim)
            concat_vas.append(concat_va)
        vjoin = ";".join(vtrims)
        ajoin = ";".join(atrims)
        cvjoin = "".join(concat_vas) + f"concat={size}:v=1:a=1[v][a]"
        trims_join = vjoin + ";" + ajoin + ";" + cvjoin + " -map [v] -map [a]"
        cmd = f"ffmpeg -y -i {file} -filter_complex {trims_join} {outfile}"
        print(cmd)
        os.system(cmd)

    def select(self, file, outfile, time_list: list):
        """
        concat multiple clip from nultiple times in one file
        :param file:
        :param time_list:
        :return:
        """
        selects = []
        size = len(time_list)
        for i in range(size):
            select = f"between(t,{time_list[i][0]},{time_list[i][1]})"
            selects.append(select)
        selects = "+".join(selects)
        trims_join = "select='" + selects + "',setpts=N/FRAME_RATE/TB;aselect='" + selects + "',asetpts=N/SR/TB"
        cmd = f"ffmpeg -y -i \"{file}\" -filter_complex {trims_join} \"{outfile}\""
        print(cmd)
        os.system(cmd)

    def concat(self, file_list, out_file):
        txt_list = []
        for file in file_list:
            file = "file '{}'".format(file)
            txt_list.append(file)
        ffmpeg_files = os.path.join(os.environ["TEMP"], "ffmpeg_file_list.txt")
        self.file_sys.write_file(txt_list, ffmpeg_files)
        cmd = f"{self.ffmpeg} -y -f concat -safe 0 -i {ffmpeg_files} -c copy {out_file}"
        print(cmd)
        os.system(cmd)
        os.remove(ffmpeg_files)

    def video_to_audio(self, video, audio):
        cmd = '%s -y -i "%s" -acodec pcm_s16le "%s"' % (self.ffmpeg, video, audio)
        print(cmd)
        os.system(cmd)

    def replace_audio(self, video, audio, new_video):
        cmd = f"{self.ffmpeg} -y -i {video}"
