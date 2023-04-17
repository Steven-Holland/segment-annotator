import numpy as np
from PyQt5.QtGui import QPixmap, QImage

def np_to_qt(img):
    h, w, c = img.shape
    nbytes = img.itemsize
    bytesPerLine = c * nbytes * w
    
    if c == 4:
        q_img = QPixmap(QImage(img.data, w, h, bytesPerLine, QImage.Format_RGBA64))
    else:
        q_img = QPixmap(QImage(img.data, w, h, bytesPerLine, QImage.Format_RGB888))
    
    return q_img
    

def addWidgets(layout, widgets, rows=0, cols=0):
    ...