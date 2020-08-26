import os
from common import python_box


class FFmpegBox:
    def __init__(self):
        self.ffmpeg = "ffmpeg"
        self.file_sys = python_box.FileSys()

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

    def trim(self, file, outfile, time_list:list):
        # todo
        """
        concat multiple clip from nultiple times in one file
        :param file:
        :param time_list:
        :return:
        """
        vtrims = []
        atrims = []
        cvtrims = []
        catrims = []
        size = len(time_list)
        for i in range(size):
            vtrim = f"[0:v]trim={time_list[i][0]}:{time_list[i][1]},setpts=PTS-STARTPTS[v{i}]"
            atrim = f"[0]atrim={time_list[i][0]}:{time_list[i][1]}[a{i}]"
            cvtrim = f"[v{i}]"
            catrim = f"[a{i}]"
            vtrims.append(vtrim)
            atrims.append(atrim)
            cvtrims.append(cvtrim)
            catrims.append(catrim)
        vjoin = ";".join(vtrims)
        ajoin = ";".join(atrims)
        cvjoin = "".join(cvtrims) + f"concat={size}[v]"
        cajoin = "".join(catrims) + f"concat={size}:v=0:a={size}[a]"
        trims_join = vjoin + ";" + ajoin +";" +  cvjoin + ";" + cajoin + " -map [v] -map [a]"
        cmd = f"ffmpeg -y -i {file} -filter_complex {trims_join} {outfile}"
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
