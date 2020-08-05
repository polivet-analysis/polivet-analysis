import logging
import sys
import trackpy
import matplotlib.pyplot as plt

from core.video import VideoLoader
from core.preprocessing import *
from core.tracking import Tracker
import core.storage
from core.analytics import Analytics

root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname).5s - %(name)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

analytics = Analytics('data.h5', 0)



