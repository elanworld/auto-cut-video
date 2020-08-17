import re
import os


class FFmpegBox:
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
        cmd = f"ffmpeg -y {jion_file} -filter_complex [0:0]concat=n={len(file_lst)}:v=0:a=1[out] -map [out] {out_file}"
        print(cmd)
        os.system(cmd)
