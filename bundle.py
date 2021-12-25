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

import setuptools
import sys
import os
import scipy
import trackpy
import PIL
from cx_Freeze import setup, Executable

__version__ = "0.9.0"

include_files = [os.path.dirname(scipy.__file__),
                 os.path.dirname(trackpy.__file__),
                 os.path.dirname(PIL.__file__),
                 ('resources/misc/data-analytics-icon-t.png', 'resources/misc/data-analytics-icon-t.png'),
                 ('resources/misc/lemur.png', 'resources/misc/lemur.png')]
excludes = ["matplotlib.tests", "numpy.random._examples"]
packages = []

base = None
if sys.platform == "win32":
    base = 'Win32GUI'

setup(
    name="polivet-analysis",
    description='Description',
    version=__version__,
    options={"build_exe": {
        'packages': packages,
        'include_files': include_files,
        'excludes': excludes
    }},
    executables=[Executable("gui_run.py", base=base)]
)
