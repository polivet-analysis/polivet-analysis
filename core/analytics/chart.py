from abc import ABC, abstractmethod
import trackpy as tp
import numpy as np
import io
from PIL import Image
import matplotlib.pyplot as plt


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


class ChartData:
    def __init__(self, trajectories_dataframe, particle_id=None):
        self.trajectories = trajectories_dataframe
        self.filtered = self.__filter_trajectories()
        self.drift = tp.compute_drift(self.filtered)

        self.disp_x = []
        self.disp_y = []

        for i in range(1, len(self.drift.x.values)):
            self.disp_x.append(self.drift.x.values[i] - self.drift.x.values[i - 1])
            self.disp_y.append(self.drift.y.values[i] - self.drift.y.values[i - 1])

        if particle_id is not None:
            self.single_trajectory = self.__get_single_trajectory(particle_id)
        else:
            self.single_trajectory = self.__get_first_single_trajectory()

    def __get_single_trajectory(self, particle_id):
        df = self.trajectories.reset_index(drop=True)
        return df.loc[df['particle'] == particle_id]

    def __get_first_single_trajectory(self):
        grouped = self.trajectories.reset_index(drop=True).groupby('particle')
        frame, track = next(iter(grouped))
        return track

    def __filter_trajectories(self):
        """ Filtering small trajectories. If trajectory is bigger than
        the value it will be removed from the set """

        filtered = tp.filter_stubs(self.trajectories, threshold=25)
        if len(filtered) > 50:
            """ For the case when there are a few trajectories we will return
            unchanged dataset. Because it will be affect the results. In case
            when there are a lot of tracks, we will remove the smaller ones
            to make the statistics more clean """
            return filtered

        return self.trajectories


class Chart(ABC):
    @abstractmethod
    def get_chart(self, data: ChartData):
        pass


class AllTrajectories(Chart):
    MAX_NUMBER_OF_TRAJECTORIES = 200_000

    def get_chart(self, data: ChartData):
        fig = plt.figure(figsize=(16, 9), dpi=300)
        ax = fig.add_subplot(1, 1, 1)
        plot = tp.plot_traj(data.filtered[:self.MAX_NUMBER_OF_TRAJECTORIES], ax=ax)
        plot_pil_image = trackpy_fig_to_pil(plot)
        fig.clear()
        plt.close(fig)
        return plot_pil_image


class XDisplacement(Chart):
    def get_chart(self, data):
        fig = plt.figure(dpi=300)
        ax = fig.add_subplot(1, 1, 1)
        ax.hist(data.disp_x, 100)
        ax.set_title('X displacement')
        ax.set_yscale('log')
        plot_pil_image = current_plt_to_fig()
        fig.clear()
        plt.close(fig)
        return plot_pil_image


class YDisplacement(Chart):
    def get_chart(self, data):
        fig = plt.figure(dpi=300)
        ax = fig.add_subplot(1, 1, 1)
        ax.hist(data.disp_y, 100)
        ax.set_title('Y displacement')
        ax.set_yscale('log')
        plot_pil_image = current_plt_to_fig()
        fig.clear()
        plt.close(fig)
        return plot_pil_image


class SingleTrajectoryStat(Chart):
    def get_chart(self, data):
        x = data.single_trajectory.x.values
        y = data.single_trajectory.y.values
        x_velocity = (x[-1] - x[0]) / len(x)
        y_velocity = (y[-1] - y[0]) / len(y)

        coeff = np.polyfit(x, y, 1)
        y_approx = coeff[0] * x + coeff[1]

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
        fig.clear()
        plt.close(fig)
        return plot_pil_image


class MSD(Chart):
    def get_chart(self, data):
        """ The logarithmic format of the graph was disabled as requested.
        If it is needed to return place this:
            - ax.set_xscale('log')
            - ax.set_yscale('log')
        """

        im = tp.imsd(data.filtered, 1, 1)
        fig = plt.figure(figsize=(16, 9), dpi=300)
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(im.index, im, 'k-', alpha=0.1)
        ax.set_title("Mean squared displacement for each particle")
        plot_pil_image = current_plt_to_fig()
        fig.clear()
        plt.close(fig)
        return plot_pil_image