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
import trackpy as tp
import pandas as pd
import threading
import matplotlib.pyplot as plt
from PIL import Image

from .chart import *


def trajectory_length(filename, particle_id):
    with tp.PandasHDFStore(filename) as store:
        df = pd.concat(iter(store))
        track = df.loc[df['particle'] == particle_id]
        return len(track.index)


class Analytics:
    def __init__(self, filename='data.h5', particle_id=None):
        self.log = logging.getLogger("Analytics")
        self.plt_lock = threading.Lock()
        with tp.PandasHDFStore(filename) as store:
            trajectories = pd.concat(iter(store))
            self.chart_data = ChartData(trajectories, particle_id)

    def analytics(self, chart: Chart):
        with self.plt_lock:
            self.log.info("Processing chart: " + type(chart).__name__)
            return chart.get_chart(self.chart_data)

    def get_all_trajectories_fig(self):
        return self.analytics(AllTrajectories())

    def get_x_displacement_fig(self):
        return self.analytics(XDisplacement())

    def get_y_displacement_fig(self):
        return self.analytics(YDisplacement())

    def get_trajectory_stat_fig(self):
        return self.analytics(SingleTrajectoryStat())

    def get_msd_for_particles_fig(self):
        return self.analytics(MSD())

    def frames_in_trajectory(self):
        track = self.chart_data.single_trajectory
        return len(track.index)  # row count

    def __frame_track_iterator(self, track, frames):
        for i, r in track.iterrows():
            try:
                f = next(frames)
                yield f, r
            except StopIteration:
                return

    def particle_movement_frames(self, frames):
        track = self.chart_data.single_trajectory

        for frame, feature in self.__frame_track_iterator(track, frames):
            with self.plt_lock:
                fig = plt.figure()
                ax = fig.add_subplot(1, 1, 1)
                ax.axis('off')
                annotated = tp.annotate(feature, frame, ax=ax)
                yield trackpy_fig_to_pil(annotated)
                fig.clear()
                plt.close(fig)

    def particle_rotating_frames(self, frames, width=200, height=200):
        track = self.chart_data.single_trajectory

        for frame, feature in self.__frame_track_iterator(track, frames):
            x_center = feature['x']
            y_center = feature['y']
            box = (x_center - (width/2), y_center - (height/2),
                   x_center + (width/2), y_center + (height/2))
            image = Image.fromarray(frame[:]).convert('L')
            yield image.crop(box)
