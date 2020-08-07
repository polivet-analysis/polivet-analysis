import h5py


def store_arrays_in_file(filename, arrays_iterator):
    with h5py.File(filename, 'w') as f:
        for i, arr in enumerate(arrays_iterator):
            dataset_id = __get_dataset_id(i)
            f.create_dataset(dataset_id, data=arr, compression='gzip')


def read_arrays_from_file(filename):
    with h5py.File(filename, 'r') as f:
        keys_count = len(f.keys())
        for i in range(keys_count):
            dataset_id = __get_dataset_id(i)
            yield f.get(dataset_id)


def __get_dataset_id(index):
    return 'arr' + str(index)
