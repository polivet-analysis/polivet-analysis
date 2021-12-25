#
#     Copyright (C) 2021  Tatiana Novosadiuk & Viktoriia Tsvetkova
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
import cv2
import numpy as np


class VideoLoader:
    def __init__(self, video_filename):
        self.video_filename = video_filename
        self.video = cv2.VideoCapture(self.video_filename)
        self.logger = logging.getLogger("VideoLoader")
        self.logger.debug('Constructor: "' + str(video_filename) + '"')

    def get_frames(self):
        """
        Method to parse video file to the sequence of frames
        :return: the generator of the frames from video file
        """

        self.logger.info('Creating video file generator')
        self.logger.debug("Reading video frame")
        self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        success, image = self.video.read()
        while success:
            yield image

            self.logger.debug("Reading video frame")
            success, image = self.video.read()

        self.logger.info('Frames loading finished')

    def get_sample_frame(self):
        self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        success, image = self.video.read()
        return image

    def get_frames_count(self):
        return int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))

    def close(self):
        self.video.release()
        cv2.destroyAllWindows()


class VideoSaver:
    def __init__(self, filename):
        self.filename = filename
        self._fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self._out = None

    def save_frames(self, frames, progress_listener=lambda *args: None):
        for index, frame in enumerate(frames):
            if self._out is None:
                width, height = frame.size
                self._out = cv2.VideoWriter(self.filename, self._fourcc, 10.0, (width, height))

            opencv_image = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
            self._out.write(opencv_image)
            progress_listener(index)
        self._out.release()
        cv2.destroyAllWindows()
