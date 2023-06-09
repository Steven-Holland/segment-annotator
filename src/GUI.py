import numpy as np
import functools

import utils
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap, QImage, QPainter, QBrush, QColor, QFont
from PyQt5.QtCore import Qt


class ImageLabel(QLabel):
    def __init__(self, img):
        super().__init__()
        
        self.img = img
        self.setPixmap(self.img)
        
        self.points = []
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.img)
        painter.setBrush(QBrush(QColor('cyan')))
        painter.setRenderHint(QPainter.Antialiasing, True)
        for pos in self.points:
            painter.drawEllipse(pos, 4, 4)
            
    def setPixmap(self, img):
        self.img = img
        return super().setPixmap(img)
    
    def clear_points(self):
        self.points.clear()
        self.update()
        
    def update_points(self, point):
        self.points.append(point)
        self.update()
        

class GUI(QWidget):
    def __init__(self, img):
        super().__init__()
        
        self.img = img
        self.height,self.width,_ = self.img.shape
        
        self.settings_layout = QHBoxLayout()
        self.center_layout = QVBoxLayout()
        self.btns_layout = QHBoxLayout()
        self.console_layout = QVBoxLayout()
        
        # Images
        self.progress_label = QLabel()
        self.image_layout = QHBoxLayout()
        self.q_img = utils.np_to_qt(img)
        self.img_label = ImageLabel(self.q_img)
        
        print('Image shape: ', self.width, self.height)
        self.mask = utils.np_to_qt(np.zeros((self.height,self.width,3)))
        self.mask_label = QLabel()
        
        # Settings bar
        self.in_label = QLabel('Input Directory: ')
        self.in_btn_browse = QPushButton(text='Browse')
        self.in_path = QLabel()
        
        self.out_label = QLabel('Output Directory: ')
        self.out_btn_browse = QPushButton(text='Browse')
        self.out_path = QLabel()
        
        self.mode_label = QLabel('Annotation Mode: ')
        self.single_point_btn = QRadioButton('Single-Point')
        self.multi_point_btn = QRadioButton('Multi-Point')
        self.box_btn = QRadioButton('Box')
        self.generate_btn = QPushButton('Generate Mask')
        self.clear_btn = QPushButton('Clear Masks')
        self.file_box = QGridLayout()
        
        # Buttons
        self.prev_btn = QPushButton('< Prev')
        self.next_btn = QPushButton('Next >')

        # Console
        self.log_box = QTextEdit(readOnly=True)
        
        
        self.main_layout = QVBoxLayout()        
        self.layout()
        
        
    def layout(self):
        
        # Settings layout
        self.in_path.setStyleSheet('border: 1px solid black;')
        self.in_path.setMinimumWidth(200)
        
        self.out_path.setStyleSheet('border: 1px solid black;')
        self.out_path.setMinimumWidth(200)
        
        self.single_point_btn.setChecked(True)
        
        self.file_box.addWidget(self.in_label, 1, 1)
        self.file_box.addWidget(self.in_path, 1, 2)
        self.file_box.addWidget(self.in_btn_browse, 1, 3)
        self.file_box.addWidget(self.out_label, 2, 1)
        self.file_box.addWidget(self.out_path, 2, 2)
        self.file_box.addWidget(self.out_btn_browse, 2, 3)
        
        self.settings_layout.addLayout(self.file_box)
        self.settings_layout.addStretch()
        self.settings_layout.addWidget(self.mode_label)
        self.settings_layout.addWidget(self.single_point_btn)
        self.settings_layout.addWidget(self.multi_point_btn)
        self.settings_layout.addWidget(self.box_btn)
        self.settings_layout.addWidget(self.generate_btn)
        self.settings_layout.addWidget(self.clear_btn)
        self.main_layout.addLayout(self.settings_layout)
        
        # Image layout
        self.mask_label.setPixmap(self.mask)
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet('font-size: 14pt;')
        
        self.center_layout.addWidget(self.progress_label)
        self.image_layout.addStretch()
        self.image_layout.addWidget(self.img_label)
        self.image_layout.addWidget(self.mask_label)
        self.image_layout.addStretch()
        self.center_layout.addLayout(self.image_layout)
        self.main_layout.addLayout(self.center_layout)
        
        # Buttons layout
        self.btns_layout.addWidget(self.prev_btn)
        self.btns_layout.addWidget(self.next_btn)
        self.main_layout.addLayout(self.btns_layout)
        
        # Console layout
        self.log_box.setMinimumHeight(200)
        self.console_layout.addWidget(self.log_box)
        self.main_layout.addLayout(self.console_layout)
        
        self.setLayout(self.main_layout)

    def clear_masks(self):
        self.mask_label.setPixmap(utils.np_to_qt(np.zeros((self.height,self.width,3))))