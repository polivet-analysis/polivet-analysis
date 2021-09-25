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

import logging
import sys
import trackpy
import matplotlib.pyplot as plt
from PIL import Image

from core.video import VideoLoader
from core.video import VideoSaver
from core.preprocessing import *
from core.tracking import Tracker
import core.storage
from core.analytics import Analytics

import matplotlib
matplotlib.use('Agg')

root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname).5s - %(name)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

analytics = Analytics('temp/data.h5', 0)


def get_frames():
    fs = core.storage.read_arrays_from_file('temp/frames.h5')
    for index, frame in enumerate(fs):
        print(index)
        for i in range(100):
            yield frame


# frames = core.storage.read_arrays_from_file('temp/frames.h5')
frames = get_frames()

movement_frames = analytics.particle_movement_frames(frames)
frames_total = analytics.frames_in_trajectory()

# frames = (Image.fromarray(frame[()]) for frame in frames)

video_saver = VideoSaver("temp/test1.mp4")


def listener(index, frames_total):
    print(index, frames_total)


video_saver.save_frames(movement_frames, lambda i: listener(i, frames_total))
