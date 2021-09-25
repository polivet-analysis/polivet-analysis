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

import sys
import os
import logging
from logging.handlers import RotatingFileHandler

LOG_DIRECTORY = 'log'

root = logging.getLogger()
root.setLevel(logging.DEBUG)
logging.getLogger("matplotlib").setLevel(logging.WARNING)

formatter = logging.Formatter('%(asctime)s - %(levelname).5s - %(name)s - %(message)s')

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
root.addHandler(console_handler)

if not os.path.exists(LOG_DIRECTORY):
    os.makedirs(LOG_DIRECTORY)
file_handler = RotatingFileHandler(LOG_DIRECTORY + '/' + 'polivet.log', maxBytes=1024 * 1024, backupCount=5)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
root.addHandler(file_handler)

logging.getLogger("MainInterface").setLevel(logging.DEBUG)

import matplotlib
matplotlib.use('Agg')

from ui.interface import MainInterface
from core.core import Core

model = Core()
main_interface = MainInterface(model)
main_interface.start()
