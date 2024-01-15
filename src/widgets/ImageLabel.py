from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPainter, QBrush, QColor
import sys
sys.path.append('..')
from utils import np_to_qt

class ImageLabel(QLabel):
    def __init__(self, img):
        super().__init__()
        
        self.setPixmap(img)
        self.points = []
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.img)
        painter.setBrush(QBrush(QColor('cyan')))
        painter.setRenderHint(QPainter.Antialiasing, True)
        for pos in self.points:
            painter.drawEllipse(pos, 4, 4)
            
    def setPixmap(self, img):
        self.img = np_to_qt(img)
        return super().setPixmap(self.img)
    
    def clear_points(self):
        self.points.clear()
        self.update()
        
    def update_points(self, point, draw=True):
        self.points.append(point)
        if draw: self.update()
        
    def get_points(self):
        points = [[p.x(), p.y()] for p in self.points]
        return points