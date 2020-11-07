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
