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
