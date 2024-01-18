import numpy as np
import cv2
from pathlib import Path
import json
from PyQt5.QtGui import QPixmap, QImage

from config import CONFIG_PATH

color_dict = {
    "white": "#FFFFFF",
    "red": "#eb3434",
    "yellow": "#ebe134",
    "green": "#34eb34"
}

def np_to_qt(img):
    h, w, c = img.shape
    nbytes = img.itemsize
    bytesPerLine = c * nbytes * w
    
    if c == 4:
        q_img = QPixmap(QImage(img.data, w, h, bytesPerLine, QImage.Format_RGBA64))
    else:
        q_img = QPixmap(QImage(img.data, w, h, bytesPerLine, QImage.Format_RGB888))
    
    return q_img

def qt_to_np(pixmap):
    img = pixmap.toImage()
    h, w, c = img.height(), img.width(), img.depth()//8
    s = img.bits().asstring(w * h * c)
    np_arr = np.fromstring(s, dtype=np.uint8).reshape((h, w, c)) 
    return np_arr

# sets and returns value of new attr
def set_attr(parent, name, val):
    setattr(parent, name, val)
    return getattr(parent, name)

def read_config_file(setting_name=None):
    with open(CONFIG_PATH, 'r') as f:
        try:
            data = json.load(f)
            if setting_name:
                data = data[setting_name]
            return data
        except:
            print('Failed to load config')
            return {}


def write_config_file(data, setting_name=None):
    new_data = data
    if setting_name:
        old_data = read_config_file()
        new_data = old_data.copy()
        new_data[setting_name] = data
    with open(CONFIG_PATH, 'w') as f:
        try:
            json.dump(new_data, f, indent=4)
        except:
            print('Failed writing to config file')
            return False
    return True