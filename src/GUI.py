import cv2
import numpy as np
import functools
from pathlib import Path
from enum import Enum
import time

import config
import utils
from sam_worker import SAM_worker
from widgets.ImageLabel import ImageLabel
from widgets.LabelSelector import LabelSelector
from labeler import Labeler

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap, QImage, QTextCursor
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot

import torch
from segment_anything import SamPredictor, sam_model_registry
cuda = torch.cuda.is_available()


class SegmentMode(Enum):
    SINGLE_POINT = 1
    MULTI_POINT = 2
    BOX = 3
        

class GUI(QWidget):
    init_sam = pyqtSignal(str)
    
    def __init__(self, in_dir: Path, out_dir: Path, resume_progress=False):
        super().__init__()
        
        # initalize sam model on separate thread
        self.sam = SAM_worker(cuda)
        self.sam_thread = QThread()
        self.sam.moveToThread(self.sam_thread)
        self.sam_thread.start(priority=QThread.TimeCriticalPriority)
        self.init_sam.connect(self.sam.config_model)
        
        self.in_dir = in_dir
        self.out_dir = out_dir
        
        self.img_idx = 0
        self.img_list = list(self.in_dir.iterdir())
        self.mask_list = list(self.out_dir.iterdir()) if resume_progress else []
        self.curr_label = ''
            
        self.img = cv2.imread(str(self.img_list[0])) if self.img_list else np.zeros((240, 320, 3))
        self.height, self.width = self.img.shape[:2]
        self.check_size()

        self.init_sam.emit(str(self.img_list[0])) if self.img_list else self.init_sam.emit('')
        
        
        self.labeler = None
        self.segment_mode = SegmentMode.SINGLE_POINT
        
        self.initUI()
        self.layout()
        
    
    def initUI(self):
        
        self.settings_layout = QHBoxLayout()
        self.center_layout = QVBoxLayout()
        self.btns_layout = QHBoxLayout()
        self.console_layout = QVBoxLayout()
        
        # Images
        self.progress_label = QLabel()
        self.image_layout = QHBoxLayout()
        self.img_label = ImageLabel(self.img)
        
        print('Image shape: ', self.width, self.height)
        self.mask = utils.np_to_qt(np.zeros((self.height,self.width,3)))
        self.mask_label = QLabel()
        
        # Side menu
        self.side_menu_layout = QVBoxLayout()
        self.label_selector_label = QLabel()
        self.label_selector = LabelSelector('Label List')
        
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
        
        self.in_path.setText(str(self.in_dir))
        self.out_path.setText(str(self.out_dir))
        self.progress_label.setText(f'1/{len(self.img_list)} images')
        self.generate_btn.setEnabled(False)
        self.prev_btn.setEnabled(False)
        
        self.in_btn_browse.clicked.connect(lambda: self.getPath('input'))
        self.out_btn_browse.clicked.connect(lambda: self.getPath('output'))
        self.next_btn.clicked.connect(self.next_image)
        self.prev_btn.clicked.connect(self.prev_image)
        self.generate_btn.clicked.connect(self.generate_mask)
        self.single_point_btn.clicked.connect(lambda: self.change_mode(SegmentMode.SINGLE_POINT))
        self.multi_point_btn.clicked.connect(lambda: self.change_mode(SegmentMode.MULTI_POINT))
        self.box_btn.clicked.connect(lambda: self.change_mode(SegmentMode.BOX))
        self.clear_btn.clicked.connect(self.clear_masks)
        self.img_label.mousePressEvent = functools.partial(self.save_segmentation_point, source_object=self.img_label.mousePressEvent)
        self.sam.ready.connect(self.sam_ready)
        self.label_selector.label_changed.connect(self.set_label)
        
        self.log(f'Cuda is available: ')
        if cuda:
            self.log('True', color='green', new_line=False)
            self.log(f'Pytorch CUDA Version is {torch.version.cuda}')
        else:
            self.log('False', color='red', new_line=False)
        self.log(f'Loading model {config.MODEL_TYPE} at checkpoint {config.CHECK_POINT}... ')
        
        
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
        
        # Menu layout
        self.side_menu_layout.addWidget(self.label_selector_label)
        self.side_menu_layout.addWidget(self.label_selector)
        self.side_menu_layout.addStretch()
        
        # Image layout
        self.mask_label.setPixmap(self.mask)
        # self.img_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        # self.image_layout.setSizeConstraint(QLayout.SetMinimumSize)
        self.img_label.setFixedHeight(self.height)
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet('font-size: 14pt;')
        
        self.center_layout.addWidget(self.progress_label)
        self.image_layout.addLayout(self.side_menu_layout)
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

        
    def getPath(self, IO):
        dlg = QFileDialog()
        path = dlg.getExistingDirectory(self, 
                                    'Browse', 
                                    str(Path.cwd())) 
        print(path)
        if path == '':
            return
        path = Path(path)
        
        if IO == 'input':
            self.in_dir = path
            self.img_idx = 0
            self.img_list.clear()
            for type in config.IMG_TYPES:
                self.img_list.extend(path.glob(type))
            
            self.next_image()
            self.in_path.setText(path)
        elif IO == 'output':
            self.out_dir = path
            self.out_path.setText(path)

    def next_image(self):
        
        if not self.prev_btn.isEnabled():
            self.prev_btn.setEnabled(True)
        
        # save mask
        img_type = self.img_list[self.img_idx].suffix[1:]
        mask_name = str(self.img_list[self.img_idx].stem) + '_mask.' + img_type
        out_file = self.out_dir / mask_name
        
        try:
            np.save(out_file, self.labeler.get_mask())
        except:
            self.log(f'Mask failed to save')
            return
        self.log(f'Mask saved to {out_file}')
        
        self.img_idx += 1
        if len(self.img_list) <= self.img_idx:
            self.log('End of dataset reached')
            self.img_idx -= 1
            self.next_btn.setEnabled(False)
            return
        
        # clear old points
        self.img_label.clear_points()
        
        # load new image
        self.img = cv2.imread(str(self.img_list[self.img_idx]))
        self.height, self.width = self.img.shape[:2]
        self.check_size()
        self.labeler.next_annotation(self.img, self.height, self.width)
        
        self.clear_masks()
        print(len(self.mask_list), self.img_idx)
        # if len(self.mask_list) > self.img_idx + 1:
        #     label = cv2.imread(str(self.mask_list[self.img_idx]))
        #     self.mask_label.setPixmap(utils.np_to_qt(label))
        
        self.progress_label.setText(f'{self.img_idx+1}/{len(self.img_list)} images')
        self.img_label.setPixmap(self.img)
    
        
    def prev_image(self):
        self.img_idx -= 1
        self.img_label.clear_points()
        
        label = cv2.imread(str(self.mask_list[self.img_idx]))
        self.mask_label.setPixmap(utils.np_to_qt(label))
        
        self.img = cv2.imread(str(self.img_list[self.img_idx]))
        self.height, self.width = self.img.shape[:2]
        self.check_size()
        self.sam.set_image(self.img)
        self.img_label.setPixmap(self.img)
        
        if not self.next_btn.isEnabled():
            self.next_btn.setEnabled(True)
            
        if self.img_idx == 0:
            self.prev_btn.setEnabled(False)
        
        self.progress_label.setText(f'{self.img_idx+1}/{len(self.img_list)} images')
        

    def save_segmentation_point(self, event, source_object=None):
        p = event.pos()
        x, y = p.x(), p.y()
        
        if (x > self.width) or (y > self.height):
            return
        elif [x,y] in self.img_label.get_points():
            self.log(f'Point ({x}, {y}) already selected for segmentation', color='yellow')
            return
        
        if self.segment_mode is SegmentMode.SINGLE_POINT:
            self.img_label.update_points(p, draw=False)
            self.generate_mask()
        else:
            self.img_label.update_points(p)
        
        
    def generate_mask(self):
        if not self.labeler: return
        
        self.labeler.generate_mask(self.img_label.get_points(),
                                   self.curr_label)
        
        if self.segment_mode is SegmentMode.SINGLE_POINT:
            self.img_label.clear_points()
        self.mask_label.setPixmap(self.labeler.get_mask_image())


    # debugging
    def mousePressEvent(self, QMouseEvent):
        p = QMouseEvent.pos()
        x,y = p.x(),p.y()
        #self.log(f'Click at ({x}, {y})')
        
        x1,y1,x2,y2 = self.img_label.rect().getCoords()
        print(x1, y1, x2, y2)
        
    def change_mode(self, mode):
        self.segment_mode = mode
        match self.segment_mode:
            case SegmentMode.SINGLE_POINT:
                self.generate_btn.setEnabled(False)
            case SegmentMode.MULTI_POINT:
                self.generate_btn.setEnabled(True)
            case SegmentMode.BOX:
                self.generate_btn.setEnabled(False)
        self.img_label.clear_points()
        
    def clear_masks(self):
        self.labeler.clear_mask()
        self.mask_label.setPixmap(utils.np_to_qt(np.zeros((self.height,self.width,3))))

    @pyqtSlot(dict)
    def set_label(self, label_info):
        self.curr_label = label_info

    @pyqtSlot(bool)
    def sam_ready(self, ret):
        self.labeler = Labeler(self.sam, self.height, self.width)
        if ret:
            self.log('Ready', color='green', new_line=False)
        else:
            self.log('Failed', color='red', new_line=False)

    def log(self, msg, color='white', new_line=True):
        text = f'''<span style=\" font-size:8pt; font-weight:400; 
        color:{utils.color_dict[color]};\" >{msg}</span>'''
        
        if new_line:
            self.log_box.append(text)
        else:
            self.log_box.moveCursor(QTextCursor.End)
            self.log_box.textCursor().insertHtml(text)
            self.log_box.moveCursor(QTextCursor.End)
            
    def check_size(self):
        if (self.img.shape[0] > config.MAX_HEIGHT) or (self.img.shape[1] > config.MAX_WIDTH):
            self.img = cv2.resize(self.img, (640, 480))
            self.width = 640
            self.height = 480
            
    def __del__(self):
        if self.sam_thread.isRunning: self.sam_thread.quit()