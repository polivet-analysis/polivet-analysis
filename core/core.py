import logging
import os
from core.video import VideoLoader
from core.video import VideoSaver
import core.preprocessing as preprocess
import core.storage as storage
from core.tracking import Tracker
from core.analytics import Analytics
from core.analytics import trajectory_length

TEMP_DIRECTORY = 'temp'
FRAMES_FILENAME = TEMP_DIRECTORY + '/' + 'frames.h5'
DATASET_FILENAME = TEMP_DIRECTORY + '/' + 'data.h5'


class Core:
    def __init__(self):
        self.log = logging.getLogger("CoreModel")
        self.brightness = -300
        self.contrast = 4.0
        self.video_filename = None
        self.video_loader = None
        self.frames_count = None

        self.tracker = None
        self.tracker_sample = None
        self.diameter = 41
        self.minmass = 20
        self.search_range = 5
        self.memory = 5

        self.analytics = None

        self.first_frame_features = None
        self.particle_index = None

        if not os.path.exists(TEMP_DIRECTORY):
            os.makedirs(TEMP_DIRECTORY)

    def load_video_file(self, filename):
        self.log.info("Loading file: " + filename)
        self.video_filename = filename
        self.video_loader = VideoLoader(self.video_filename)

    def set_brightness_contrast(self, brightness, contrast):
        self.brightness = brightness
        self.contrast = contrast

    def sample_frame_from_video(self):
        if self.video_loader is None:
            raise Exception("Wrong model state: video filename not set")

        sample_frame = self.video_loader.get_sample_frame()
        sample_frame = next(preprocess.apply_grayscale([sample_frame]))
        sample_frame = next(preprocess.apply_contrast([sample_frame],
                                                      self.contrast, self.brightness))
        return sample_frame

    def get_frames_count(self):
        if self.video_loader is None:
            raise Exception("Wrong model state: video filename not set")

        if self.frames_count is None:
            self.frames_count = self.video_loader.get_frames_count()

        return self.frames_count

    def start_contrast_process(self, progress_listener):
        if self.video_loader is None:
            raise Exception("Wrong model state: video filename not set")

        frames = self.video_loader.get_frames()
        grayscale = preprocess.apply_grayscale(frames)
        contrast = preprocess.apply_contrast(grayscale, self.contrast, self.brightness)

        def progress_wrapper(iterator, total_count):
            for index, item in enumerate(iterator):
                progress_listener(index, total_count)
                yield item

        # def limiter(iterator):
        #     for index, item in enumerate(iterator):
        #         if index > 20:
        #             break
        #         yield item

        # contrast = limiter(contrast)
        # self.frames_count = 20
        self.frames_count = self.get_frames_count()
        wrapped = progress_wrapper(contrast, self.frames_count)
        storage.store_arrays_in_file(FRAMES_FILENAME, wrapped)

    def create_tracker(self):
        self.tracker = Tracker()
        self.tracker_sample = self.sample_frame_from_video()
        self.log.info("Tracker created")

    def set_diameter_minmass(self, diameter, minmass):
        self.diameter = diameter
        self.minmass = minmass

    def get_annotated_sample(self):
        if self.tracker is None:
            raise Exception("Wrong model state: tracker not set")

        features = self.tracker.locate_on_frame(self.tracker_sample, self.diameter, self.minmass)
        self.first_frame_features = features
        return self.tracker.get_annotated_image(self.tracker_sample, features)

    def start_locate_process(self, progress_listener):
        if self.tracker is None:
            raise Exception("Wrong model state: tracker not set")

        frames = storage.read_arrays_from_file(FRAMES_FILENAME)
        self.tracker.locate_particles(frames, self.diameter, self.minmass, DATASET_FILENAME,
                                      lambda i: progress_listener(i, self.frames_count))

    def set_range_memory(self, search_range, memory):
        self.search_range = search_range
        self.memory = memory

    def start_linkage_process(self, progress_listener):
        if self.tracker is None:
            raise Exception("Wrong model state: tracker not set")

        self.tracker.link_trajectories(self.search_range, self.memory, DATASET_FILENAME,
                                       lambda i: progress_listener(i, self.frames_count))

    def get_annotated_sample_choose_particle(self, x_on_frame, y_on_frame):
        if self.tracker is None:
            raise Exception("Wrong model state: tracker not set")

        if self.first_frame_features is None:
            self.log.info("Locating features for first frame particle choose process")
            self.first_frame_features = self.tracker.locate_on_frame(self.tracker_sample,
                                                                     self.diameter, self.minmass)

        self.particle_index = self.tracker.locate_particle_by_coords(self.first_frame_features, x_on_frame, y_on_frame)
        return self.tracker.get_annotated_image(self.tracker_sample, self.first_frame_features, self.particle_index)

    def get_trajectory_length_of_chosen_particle(self):
        return trajectory_length(DATASET_FILENAME, self.particle_index)

    def create_analytics(self):
        self.analytics = Analytics(DATASET_FILENAME, self.particle_index)
        return self.analytics

    def get_analytics(self):
        return self.analytics

    def start_save_movement_video_process(self, filename, progress_listener):
        if self.analytics is None:
            raise Exception("Wrong model state: analytics not set")

        analytics = self.get_analytics()
        frames = storage.read_arrays_from_file(FRAMES_FILENAME)

        movement_frames = analytics.particle_movement_frames(frames)
        frames_total = analytics.frames_in_trajectory()

        video_saver = VideoSaver(filename)
        video_saver.save_frames(movement_frames, lambda i: progress_listener(i, frames_total))

    def start_save_rotation_video_process(self, filename, progress_listener):
        if self.analytics is None:
            raise Exception("Wrong model state: analytics not set")

        analytics = self.get_analytics()
        frames = storage.read_arrays_from_file(FRAMES_FILENAME)

        movement_frames = analytics.particle_rotating_frames(frames, 200, 200)
        frames_total = analytics.frames_in_trajectory()

        video_saver = VideoSaver(filename)
        video_saver.save_frames(movement_frames, lambda i: progress_listener(i, frames_total))
