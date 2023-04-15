import numpy as np

import utils
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap, QImage

class GUI(QWidget):
    def __init__(self, img):
        super().__init__()
        
        self.img = img
        self.height,self.width,_ = self.img.shape
        
        self.image_layout = QHBoxLayout()
        self.settings_layout = QHBoxLayout()
        self.btns_layout = QHBoxLayout()
        self.console_layout = QVBoxLayout()
        
        # Images
        self.q_img = utils.np_to_qt(img)
        self.label_img = QLabel()
        
        print('Image shape: ', self.width, self.height)
        self.mask = utils.np_to_qt(np.zeros((self.height,self.width,3)))
        self.label_mask = QLabel()
        
        # Settings bar
        self.in_label = QLabel('Input Directory: ')
        self.in_btn_browse = QPushButton(text='Browse')
        self.in_path = QLabel()
        
        self.out_label = QLabel('Output Directory: ')
        self.out_btn_browse = QPushButton(text='Browse')
        self.out_path = QLabel()
        
        self.spacer = QLabel()
        self.btn_multi = QCheckBox('Multi-Mask')
        self.file_box = QGridLayout()
        
        # Buttons
        self.btn_prev = QPushButton('< Prev')
        self.btn_next = QPushButton('Next >')

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
        
        self.spacer.setFixedWidth(int(400))
        
        self.file_box.addWidget(self.in_label, 1, 1)
        self.file_box.addWidget(self.in_path, 1, 2)
        self.file_box.addWidget(self.in_btn_browse, 1, 3)
        self.file_box.addWidget(self.out_label, 2, 1)
        self.file_box.addWidget(self.out_path, 2, 2)
        self.file_box.addWidget(self.out_btn_browse, 2, 3)
        
        self.settings_layout.addLayout(self.file_box)
        self.settings_layout.addWidget(self.spacer)
        self.settings_layout.addWidget(self.btn_multi)
        self.main_layout.addLayout(self.settings_layout)
        
        # Image layout
        self.label_img.sizePolicy().setVerticalPolicy(QSizePolicy.Ignored)
        self.label_img.setPixmap(self.q_img)
        self.label_mask.setPixmap(self.mask)
        
        self.image_layout.addWidget(self.label_img)
        self.image_layout.addWidget(self.label_mask)
        self.main_layout.addLayout(self.image_layout)
        
        # Buttons layout
        self.btns_layout.addWidget(self.btn_prev)
        self.btns_layout.addWidget(self.btn_next)
        self.main_layout.addLayout(self.btns_layout)
        
        # Console layout
        self.log_box.setMinimumHeight(200)
        self.console_layout.addWidget(self.log_box)
        self.main_layout.addLayout(self.console_layout)
        
        self.setLayout(self.main_layout)

    def draw_point(self, point):
        ...