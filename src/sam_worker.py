import numpy as np
import cv2
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from segment_anything import SamPredictor, sam_model_registry
from fastsam import FastSAM, FastSAMPrompt
from utils import smart_resize
from config import MODEL_TYPE, SAM_CHECK_POINT, FAST_SAM_CHECK_POINT, MAX_HEIGHT, MAX_WIDTH
import time


class FastSAMWorker(QObject):
    ready = pyqtSignal(bool)
    
    def __init__(self, cuda, parent=None):
        super(self.__class__, self).__init__(parent)
        self.device = 'cuda' if cuda else 'cpu'
        self.configured = False
        self.check_point = FAST_SAM_CHECK_POINT
    
    @pyqtSlot(str)
    def config_model(self, img_path):
        start = time.time()
        try:
            self.model = FastSAM(self.check_point, task='segment')
        except:
            self.ready.emit(self.configured)
            return

        self.configured = True
        self.set_image(img_path)
        print(f'Config Time: {time.time() - start}')
        self.ready.emit(self.configured)
    
    def set_image(self, img_path):
        if not self.configured: return
        results = self.model(img_path, 
                            device=self.device, 
                            retina_masks=True,
                            verbose=False, 
                            imgsz=1024, 
                            conf=0.25,
                            iou=0.9)
        self.predictor = FastSAMPrompt(img_path, results, device=self.device)
    
    def predict(self, point_coords=None, point_labels=None):
        if not self.configured: return []
        return self.predictor.point_prompt(points=point_coords,
                                           pointlabel=point_labels)
    
    def __str__(self):
        return 'FastSAM'


class SAMWorker(QObject):
    ready = pyqtSignal(bool)
    
    def __init__(self, cuda, parent=None):
        super(self.__class__, self).__init__(parent)
        self.cuda = cuda
        self.configured = False
        self.check_point = SAM_CHECK_POINT
    
    @pyqtSlot(str)
    def config_model(self, img_path):
        start = time.time()
        try:
            self.sam = sam_model_registry[MODEL_TYPE](self.check_point)
        except:
            self.ready.emit(self.configured)
            return
        if self.cuda: self.sam.to(device='cuda')
        self.predictor = SamPredictor(self.sam)
        self.configured = True
        self.set_image(img_path)
        print(f'Config Time: {time.time() - start}')
        self.ready.emit(self.configured)
    
    def set_image(self, img_path):
        img = cv2.imread(img_path)
        img = smart_resize(img, (MAX_WIDTH, MAX_HEIGHT))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        if self.configured: self.predictor.set_image(img)
    
    def predict(self, *args, **kwargs):
        if not self.configured: return []
        masks, scores, logits = self.predictor.predict(*args, **kwargs)
        return masks
    
    def __str__(self):
        return 'SAM'


            
    