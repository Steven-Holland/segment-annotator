import sys
import os
import glob
import cv2
import numpy as np
import functools

import config
import utils

from GUI import GUI
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap, QImage

import torch
import torchvision
from segment_anything import SamPredictor, sam_model_registry
cuda = torch.cuda.is_available()


class MainWindow(QMainWindow):
    def __init__(self, in_dir, out_dir):
        super().__init__()
        
        self.in_dir = in_dir
        self.out_dir = out_dir
        self.img_idx = 1 
        self.img_list = os.listdir(in_dir)
        self.img = cv2.imread(os.path.join(in_dir, self.img_list[0]))
        self.height, self.width = self.img.shape[:2]
        self.check_size()
        
        self.segmentation_points = []

        self.gui = GUI(self.img)
        self.setCentralWidget(self.gui)
        
        self.gui.in_btn_browse.clicked.connect(lambda: self.getPath('input'))
        self.gui.out_btn_browse.clicked.connect(lambda: self.getPath('output'))
        self.gui.btn_next.clicked.connect(self.nextImage)
        self.gui.label_img.mousePressEvent = functools.partial(self.save_segmentation_point, source_object=self.gui.label_img.mousePressEvent)
        
        self.setGeometry(200, 100, 800, 500)
        self.setWindowTitle("Labeler")
        
        self.config_model()
        
        
    def config_model(self):
        self.sam = sam_model_registry[config.MODEL_TYPE](config.CHECK_POINT)
        
        self.log(f'Cuda is available: {cuda}')
        if cuda:
            self.log(f'Pytorch CUDA Version is {torch.version.cuda}')
            self.sam.to(device='cuda')
            
        self.log(f'Loading model {config.MODEL_TYPE} at checkpoint {config.CHECK_POINT}\n')
            
        self.predictor = SamPredictor(self.sam)
        self.predictor.set_image(self.img, 'BGR')
        
    def getPath(self, IO):
        dlg = QFileDialog()
        path = dlg.getOpenFileName(self, 
                                    'Browse', 
                                    os.getcwd(), 
                                    f"Images ({' '.join(config.IMG_TYPES)})") 
        path = path[0]
        print(path)
        if path == '':
            return
        
        if IO == 'input':
            self.in_dir = path
            self.img_idx = 0
            self.img_list.clear()
            for type in config.IMG_TYPES:
                self.img_list.extend(glob.glob(os.path.join(path, type)))
            
            self.nextImage()
            self.gui.in_path.setText(path)
        elif IO == 'output':
            self.out_dir = path
            self.gui.out_path.setText(path)

    def nextImage(self):
        self.img = cv2.imread(os.path.join(self.in_dir, self.img_list[self.img_idx]))
        self.check_size()
        self.predictor.set_image(self.img, 'BGR')
        
        self.gui.label_mask.pixmap().save(os.path.join(self.out_dir, self.img_list[self.img_idx][-4]), 'PNG')
        self.gui.label_mask.setPixmap(utils.np_to_qt(np.zeros((self.height,self.width,3))))
        self.gui.label_img.setPixmap(utils.np_to_qt(self.img))
        self.img_idx += 1

    def save_segmentation_point(self, event, source_object=None):
        p = event.pos()
        x, y = p.x(), p.y()
        
        if (x > self.width) or (y > self.height()):
            return
        elif [x,y] in self.segmentation_points:
            self.log(f'Point ({x}, {y}) already selected for segmentation')
            return
            
        self.segmentation_points.append([x,y])

    def mousePressEvent(self, QMouseEvent):
        p = QMouseEvent.pos()
        x,y = p.x(),p.y()
        self.log(f'Click at ({x}, {y})')
        
        x1,y1,x2,y2 = self.gui.label_img.rect().getCoords()
        print(x1, y1, x2, y2)
        
    def log(self, msg):
        self.gui.log_box.append(msg)
        
    def check_size(self):
        if (self.img.shape[0] > config.MAX_HEIGHT) or (self.img.shape[1] > config.MAX_WIDTH):
            self.img = cv2.resize(self.img, (640, 480))
            self.width = 640
            self.height = 480
        
        
    

def main():
    
    app = QApplication(sys.argv)
    
    window = MainWindow(in_dir=R'../imgs/in', out_dir=R'../imgs/out')
    window.show()
    
    sys.exit(app.exec_())
    
    
    
    return
    sam = sam_model_registry[MODEL_TYPE](CHECK_POINT)
    sam.to(device=DEVICE)
    predictor = SamPredictor(sam)
    
    img = cv2.imread('./imgs/test.png')
    print('Image Shape: ', img.shape)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    def show_mask(mask):
        color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
        h, w = mask.shape[-2:]
        mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
        cv2.imshow('mask', mask_image)
        
    

    def click(event, x, y, flags, params):
        # checking for left mouse clicks
        if event in [cv2.EVENT_LBUTTONDOWN, cv2.EVENT_RBUTTONDOWN]:
            predictor.set_image(img)
            masks, scores, logits = predictor.predict(point_coords=np.array([[x, y]]), point_labels=np.array([1]))
            print(x, y)
            show_mask(masks[0])
            

    
    cv2.imshow('img', img)
    cv2.setMouseCallback('img', click)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    
    
    
    
    
if __name__ == '__main__':
    main()