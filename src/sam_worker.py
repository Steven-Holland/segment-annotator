
import numpy as np
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from segment_anything import SamPredictor, sam_model_registry
import config

class SAM_worker(QObject):
    ready = pyqtSignal(bool)
    
    def __init__(self, cuda, parent=None):
        super(self.__class__, self).__init__(parent)
        self.cuda = cuda
        self.configured = False
    
    @pyqtSlot(np.ndarray)
    def config_model(self, img):
        try:
            self.sam = sam_model_registry[config.MODEL_TYPE](config.CHECK_POINT)
        except:
            self.ready.emit(self.configured)
            return
        if self.cuda: self.sam.to(device='cuda')

        self.predictor = SamPredictor(self.sam)
        self.configured = True
        self.set_image(img)
        self.ready.emit(self.configured)
    
    def set_image(self, img):
        if self.configured: self.predictor.set_image(img, 'BGR')
    
    def predict(self, *args, **kwargs):
        if not self.configured: return ([], [], [])
        return self.predictor.predict(*args, **kwargs)
            
    