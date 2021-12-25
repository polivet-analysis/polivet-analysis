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

import cv2
import numpy as np


def apply_grayscale(frames):
    """
    Applying grayscale transformtaion to frames

    :param frames: input iterator
    :return: generator of the transformed frames
    """
    def to_grayscale(image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    return (to_grayscale(frame) for frame in frames)


def apply_contrast(frames, multiplier, displacement):
    """
    Applies contrast to frame generator

    :param frames:
    :param multiplier:
    :param displacement:
    :return: generator of the contrasted items
    """
    def contrast_image(source, multiplier, displacement):
        contrasted = multiplier * source + displacement
        contrasted = np.clip(contrasted, 0, 255)
        return contrasted

    return (contrast_image(frame, multiplier, displacement) for frame in frames)

