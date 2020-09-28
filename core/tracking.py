import logging
import trackpy
import io
from PIL import Image
import matplotlib.pyplot as plt


class Tracker:
    def __init__(self):
        self.log = logging.getLogger('Tracker')

    def locate_on_frame(self, frame, diameter, minmass):
        self.log.debug("Locating particles on frame. [" + str(diameter) + ", " + str(minmass) + "]")
        return trackpy.locate(frame, diameter, minmass=minmass, invert=True)

    def get_annotated_image(self, frame, features, highlight_index=None):
        self.log.debug("Annotating image with features")
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.axis('off')
        annotated = trackpy.annotate(features, frame, ax=ax)

        if highlight_index is not None:
            single = features.iloc[highlight_index]
            annotated = trackpy.annotate(single, frame, color='#3c4648', ax=annotated,
                                         plot_style={'markersize': 20})

        figure = annotated.get_figure()
        buffer = io.BytesIO()
        figure.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        plt.close(figure)
        return Image.open(buffer)

    def locate_particles(self, frames, diameter, minmass, filename='data.h5',
                         progress_listener=lambda *args: None):
        self.log.info('Starting particle tracking to file: ' + filename)
        with trackpy.PandasHDFStore(filename, t_column='frame', mode='w') as s:
            for i, image in enumerate(frames):
                features = self.locate_on_frame(image, diameter, minmass)
                features['frame'] = i
                s.put(features)
                progress_listener(i)
        self.log.info('Particles located')
        return self

    def batch_locate_particles(self, frames, diameter, minmass, filename='data.h5',
                               progress_listener=lambda *args: None):
        self.log.info('Starting particle tracking to file: ' + filename)
        self.log.info('Diameter: ' + str(diameter) + "; Minmass: " + str(minmass))

        def batches_gen(iterator, size):
            batch = []
            i = 0
            for item in iterator:
                batch.append(item)
                i += 1

                if i == size:
                    yield batch
                    batch = []
                    i = 0

        with trackpy.PandasHDFStore(filename, t_column='frame') as s:
            for batch in batches_gen(frames, 5):
                trackpy.batch(batch, diameter, minmass=minmass, invert=True,
                              output=s, engine='numba')
        self.log.info('Particles located')
        return self

    def link_trajectories(self, search_range, memory, filename='data.h5',
                          progress_listener=lambda *args: None):
        self.log.info('Linking particles in file "' + filename + '"')
        with trackpy.PandasHDFStore(filename) as store:
            i = 0
            for linked in trackpy.link_df_iter(store, search_range, memory=memory):
                store.put(linked)
                progress_listener(i)
                i += 1
        return self

    def locate_particle_by_coords(self, features, x_on_frame, y_on_frame):
        def distance(x1, y1, x2, y2):
            return (x2 - x1)**2 + (y2 - y1)**2

        min_d = None
        min_index = None
        for index, row in features.iterrows():
            x, y = row['x'], row['y']
            d = distance(x, y, x_on_frame, y_on_frame)
            if min_d is None or d < min_d:
                min_d = d
                min_index = index

        return min_index
