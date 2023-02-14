from moviepy.editor import *
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import os

def get_duration(filename):
	clip = VideoFileClip(filename)
	return clip.duration, clip.fps

def trim(path):
	ffmpeg_extract_subclip(path, 0, 600, targetname="./data/start.mp4")
	duration, fps = get_duration(path)
	ffmpeg_extract_subclip(path, duration - 600, duration, targetname="./data/end.mp4")
	#os.remove(path);
	return fps
		
