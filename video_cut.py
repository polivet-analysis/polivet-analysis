from PIL import Image
from core.video import VideoLoader
from core.video import VideoSaver

video_filename = "C:/home/one-drive/projects/veterinars-polivet/1.mp4"
output_filename = "C:/home/one-drive/projects/veterinars-polivet/test_100_frames.mp4"
number_of_frames = 100

loader = VideoLoader(video_filename)
frames_gen = loader.get_frames()
frames_limited = [Image.fromarray(next(frames_gen)) for _ in range(number_of_frames)]

saver = VideoSaver(output_filename)
saver.save_frames(frames_limited)