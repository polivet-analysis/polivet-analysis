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
