# auto-cut-video
auto cut video to a clip what save climax of oringin vidweo file
# 介绍
- 智能选取一段视频的高潮部分，对选取的部分进行二次切割，识别切割出每一个转场，并将所有部分和随机的音频合并，形成二次创作视频(短视频)
1. 能节省大量的手工剪辑
2. 识别高潮
3. 识别切割场景
4. 可不费力自动剪辑出作品发布
# 使用指南
1. 安装ffmpeg，[ffmpeg官网地址](https://ffmpeg.org) ，并配置环境变量。
2. python moveo_cut.py video_dir bgm_dir # video_dir:剪辑源视频所在目录 bgm_dir：背景音乐所在目录
3. 或者编辑代码中配置的路径，直接运行即可
# 分享
目前为自动剪视频，后续希望有自动上传视频到B站，抖音功能，自动化一步到位，自动赚钱也一部到位😀，分享的出来希望大家多多支持，贡献想法方法。

## 补充
- main_short_cut.py : 短视频剪辑
- main_speech_recognize.py : 切除非说话片段（录音场景）
- main_pic_with_audio.py : 批量图片匹配音频节奏to视频
 
 