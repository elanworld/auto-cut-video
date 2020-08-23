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
