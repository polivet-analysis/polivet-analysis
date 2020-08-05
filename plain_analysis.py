import trackpy as tp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cv2
import glob


def contrast_image(source):
    contrasted = 4.0 * source - 300
    for i in range(len(contrasted)):
        for j in range(len(contrasted[i])):
            if contrasted[i][j] > 255:
                contrasted[i][j] = 255
    return contrasted


def load_frames_from_video_file(video_filename, frames_number=100):
    print("Reading frames from file ", video_filename)
    video = cv2.VideoCapture(video_filename)

    frames = []
    for img_n in range(frames_number):
        _, image = video.read()
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        contrasted_image = contrast_image(gray_image)
        frames.append(contrasted_image)
        print("Reading frame №", img_n + 1)

    return frames


def process_frames_from_video_to_png(video_filename, output_filenames):
    print("Processing images from file", video_filename)
    video = cv2.VideoCapture(video_filename)

    files_processed = 0
    success, image = video.read()
    while success:
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        contrasted_image = contrast_image(gray_image)
        cv2.imwrite(output_filenames + '-' + str(files_processed) + '.png', contrasted_image)
        files_processed += 1
        print("Processed %d files" % files_processed)
        success, image = video.read()


def load_frames_from_directory(images_placeholder, frames_count=0):
    filenames = glob.glob(images_placeholder)
    filenames.sort()
    if frames_count != 0: filenames = filenames[:frames_count]
    return [cv2.imread(img, cv2.IMREAD_GRAYSCALE) for img in filenames]

# process_frames_from_video_to_png('resources/flux.mp4', 'resources/image/flux')
# frames = load_frames_from_directory('resources/image/flux-*.png', 400)

# print("Extracting features from frames")
# with tp.PandasHDFStore('data.h5') as store:
#    tp.batch(frames, 41, minmass=20, invert=True, output=store)

# print("Linking features to trajectories")
# with tp.PandasHDFStore('data.h5') as store:
#    for linked in tp.link_df_iter(store, 5, memory=3):
#        store.put(linked)

# print("Visualizing trajectories")
# with tp.PandasHDFStore('data.h5') as store:
#     trajectories = pd.concat(iter(store))
#     tp.plot_traj(trajectories)

# f.head()
# tp.annotate(f, frames[0], plot_style={'markersize': 1})
# plt.imshow(contrasted, cmap='inferno', vmin=0, vmax=255)
# plt.show()


def single_track_analysis(track):
    x = track.x.values
    y = track.y.values
    x_velocity = (x[-1] - x[0]) / len(x)
    y_velocity = (y[-1] - y[0]) / len(y)

    coeff = np.polyfit(x, y, 1)
    y_approx = coeff[0] * x + coeff[1]
    plt.figure(dpi=300)
    plt.plot(x, y, label='single track')
    plt.plot(x, y_approx, label='linear approximation')
    plt.gca().invert_yaxis()
    plt.xlabel('x [px]')
    plt.ylabel('y [px]')
    plt.legend(frameon=False)
    plt.text(901, 30, "Average x displacement: %.4f px/fm" % (x_velocity))
    plt.text(901, 30.5, "Average y displacement: %.4f px/fm" % (y_velocity))
    plt.axes([0.2, 0.2, .3, .3])

    squared_displacements = []
    a = coeff[0]
    for i in range(len(x)):
        disp = (1 / (1 + a ** 2)) * ((y[i] - y_approx[i]) ** 2) / len(x)
        squared_displacements.append(disp)
    plt.title('MSD')
    plt.hist(squared_displacements, 100)
    plt.show()


with tp.PandasHDFStore('data.h5') as store:
    trajectories = pd.concat(iter(store))
    #filtered = tp.filter_stubs(trajectories)
    filtered = trajectories
    drift = tp.compute_drift(filtered)

    im = tp.imsd(filtered, 1, 1)
    plt.plot(im.index, im, 'k-', alpha=0.1)
    plt.xscale('log')
    plt.yscale('log')
    plt.title("Mean squared displacement for each particle")
    plt.show()

    disp_x = []
    disp_y = []
    for i in range(1, len(drift.x.values)):
        disp_x.append(drift.x.values[i] - drift.x.values[i - 1])
        disp_y.append(drift.y.values[i] - drift.y.values[i - 1])

    plt.figure(dpi=300)
    plt.hist(disp_x, 100)
    plt.title('X displacement')
    plt.yscale('log')
    plt.show()

    plt.figure(dpi=300)
    plt.hist(disp_y, 100)
    plt.yscale('log')
    plt.title('Y displacement')
    plt.show()

    grouped = filtered.reset_index(drop=True).groupby('particle')
    frame, track = next(iter(grouped))
    single_track_analysis(track)

    tp.plot_traj(filtered)
