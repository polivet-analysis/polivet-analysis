import trackpy as tp
import pandas as pd
import numpy as np
import io
import threading
import matplotlib.pyplot as plt
from PIL import Image


def trackpy_fig_to_pil(plot):
    fig = plot.get_figure()
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    return Image.open(buffer)


def current_plt_to_fig():
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    return Image.open(buffer)


def trajectory_length(filename, particle_id):
    with tp.PandasHDFStore(filename) as store:
        df = pd.concat(iter(store))
        track = df.loc[df['particle'] == particle_id]
        return len(track.index)


class Analytics:
    def __init__(self, filename='data.h5', particle_id=None):
        self.particle_id = particle_id
        self.trajectories = None
        self.filtered = None
        self.drift = None

        self.plt_lock = threading.Lock()

        with tp.PandasHDFStore(filename) as store:
            self.trajectories = pd.concat(iter(store))
            # self.filtered = tp.filter_stubs(self.trajectories)
            self.filtered = self.trajectories
            self.drift = tp.compute_drift(self.filtered)

        self.disp_x = []
        self.disp_y = []

        for i in range(1, len(self.drift.x.values)):
            self.disp_x.append(self.drift.x.values[i] - self.drift.x.values[i - 1])
            self.disp_y.append(self.drift.y.values[i] - self.drift.y.values[i - 1])

    def __get_single_trajectory(self):
        if self.particle_id is not None:
            df = self.filtered.reset_index(drop=True)
            return df.loc[df['particle'] == self.particle_id]

        grouped = self.filtered.reset_index(drop=True).groupby('particle')
        frame, track = next(iter(grouped))
        return track

    def frames_in_trajectory(self):
        track = self.__get_single_trajectory()
        return len(track.index) # row count

    def get_all_trajectories_fig(self):
        with self.plt_lock:
            fig = plt.figure(figsize=(16, 9), dpi=300)
            ax = fig.add_subplot(1, 1, 1)
            plot = tp.plot_traj(self.trajectories, ax=ax)
            plot_pil_image = trackpy_fig_to_pil(plot)
            plt.close(fig)
            return plot_pil_image

    def get_x_displacement_fig(self):
        with self.plt_lock:
            fig = plt.figure(dpi=300)
            ax = fig.add_subplot(1, 1, 1)
            ax.hist(self.disp_x, 100)
            ax.set_title('X displacement')
            ax.set_yscale('log')
            plot_pil_image = current_plt_to_fig()
            plt.close(fig)
            return plot_pil_image

    def get_y_displacement_fig(self):
        with self.plt_lock:
            fig = plt.figure(dpi=300)
            ax = fig.add_subplot(1, 1, 1)
            ax.hist(self.disp_y, 100)
            ax.set_title('Y displacement')
            ax.set_yscale('log')
            plot_pil_image = current_plt_to_fig()
            plt.close(fig)
            return plot_pil_image

    def get_trajectory_stat_fig(self):
        track = self.__get_single_trajectory()
        x = track.x.values
        y = track.y.values
        x_velocity = (x[-1] - x[0]) / len(x)
        y_velocity = (y[-1] - y[0]) / len(y)

        coeff = np.polyfit(x, y, 1)
        y_approx = coeff[0] * x + coeff[1]
        with self.plt_lock:
            fig = plt.figure(dpi=300)
            ax = fig.add_subplot(1, 1, 1)
            ax.plot(x, y, label='single track')
            ax.plot(x, y_approx, label='linear approximation')
            ax.invert_yaxis()
            ax.set_xlabel('x [px]')
            ax.set_ylabel('y [px]')
            ax.legend(frameon=False)
            ax.text(901, 30, "Average x displacement: %.4f px/fm" % (x_velocity))
            ax.text(901, 30.5, "Average y displacement: %.4f px/fm" % (y_velocity))
            subax = fig.add_axes([.18, .18, .23, .23])

            squared_displacements = []
            a = coeff[0]
            for i in range(len(x)):
                disp = (1 / (1 + a ** 2)) * ((y[i] - y_approx[i]) ** 2) / len(x)
                squared_displacements.append(disp)
            subax.set_title('MSD')
            subax.hist(squared_displacements, 100)
            plot_pil_image = current_plt_to_fig()
            plt.close(fig)
            return plot_pil_image

    def get_msd_for_particles_fig(self):
        im = tp.imsd(self.filtered, 1, 1)
        with self.plt_lock:
            fig = plt.figure(figsize=(16, 9), dpi=300)
            ax = fig.add_subplot(1, 1, 1)
            ax.plot(im.index, im, 'k-', alpha=0.1)
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.set_title("Mean squared displacement for each particle")
            plot_pil_image = current_plt_to_fig()
            plt.close(fig)
            return plot_pil_image

    def __frame_track_iterator(self, track, frames):
        for i, r in track.iterrows():
            f = next(frames)
            yield f, r

    def particle_movement_frames(self, frames):
        track = self.__get_single_trajectory()

        for frame, feature in self.__frame_track_iterator(track, frames):
            with self.plt_lock:
                fig = plt.figure()
                ax = fig.add_subplot(1, 1, 1)
                ax.axis('off')
                annotated = tp.annotate(feature, frame, ax=ax)
                yield trackpy_fig_to_pil(annotated)
                plt.close(fig)

    def particle_rotating_frames(self, frames, width=200, height=200):
        track = self.__get_single_trajectory()

        for frame, feature in self.__frame_track_iterator(track, frames):
            x_center = feature['x']
            y_center = feature['y']
            box = (x_center - (width/2), y_center - (height/2),
                   x_center + (width/2), y_center + (height/2))
            image = Image.fromarray(frame[:]).convert('L')
            yield image.crop(box)
