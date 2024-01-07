
import numpy as np
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from segment_anything import SamPredictor, sam_model_registry
import config

class SAM_worker(QObject):
    ready = pyqtSignal()
    
    def __init__(self, cuda, parent=None):
        super(self.__class__, self).__init__(parent)
        self.cuda = cuda
    
    @pyqtSlot(np.ndarray)
    def config_model(self, img):
        self.sam = sam_model_registry[config.MODEL_TYPE](config.CHECK_POINT)
        if self.cuda: self.sam.to(device='cuda')

        self.predictor = SamPredictor(self.sam)
        self.set_image(img)
        self.ready.emit()
    
    def set_image(self, img):
        self.predictor.set_image(img, 'BGR')
    
    def predict(self, *args, **kwargs):
        return self.predictor.predict(*args, **kwargs)
            
    