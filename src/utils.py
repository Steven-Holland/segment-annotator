import numpy as np
from PyQt5.QtGui import QPixmap, QImage

def np_to_qt(img):
    h, w, c = img.shape
    bytesPerLine = 3 * w
    q_img = QPixmap(QImage(img.data, w, h, bytesPerLine, QImage.Format_RGB888))
    
    return q_img

def addWidgets(layout, widgets, rows=0, cols=0):
    ...