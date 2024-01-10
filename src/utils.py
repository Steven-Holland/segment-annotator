import numpy as np
import cv2
from PyQt5.QtGui import QPixmap, QImage

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