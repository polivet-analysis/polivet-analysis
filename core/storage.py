import h5py


def store_arrays_in_file(filename, arrays_iterator):
    with h5py.File(filename, 'w') as f:
        for i, arr in enumerate(arrays_iterator):
            f.create_dataset('arr' + str(i), data=arr, compression='gzip')


def read_arrays_from_file(filename):
    with h5py.File(filename, 'r') as f:
        for key in f.keys():
            yield f.get(key)
