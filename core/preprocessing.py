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

