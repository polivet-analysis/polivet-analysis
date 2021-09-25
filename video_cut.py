#
#     Copyright (C) 2021  Tatiana Novosadjuk & Victoria Tsvetkova
#
#     This file is part of Polevet-SPb-2020.
#
#     Polevet-SPb-2020 is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     Polevet-SPb-2020 is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with Polevet-SPb-2020.  If not, see <https://www.gnu.org/licenses/>.
#

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