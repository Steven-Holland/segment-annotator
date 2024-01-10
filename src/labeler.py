import numpy as np
import cv2
from PyQt5.QtCore import QObject
from enum import Enum
from sam_worker import SAM_worker

class SegmentMode(Enum):
    SINGLE_POINT = 1
    MULTI_POINT = 2
    BOX = 3


class Annotation:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.mask = np.zeros((height, width, 3))

    def append(self, new_mask, label):
        new_mask = np.where(new_mask, label)
        self.mask = np.where(new_mask, new_mask, self.mask)
        
    def get_mask(self):
        return self.mask
        
        
    def __len__(self):
        return len(self.masks)
    


class Labeler(QObject):
    def __init__(self, sam: SAM_worker):
        super().__init__()
        self.sam = sam
        self.annotations = []
        self.segment_mode = SegmentMode.SINGLE_POINT
        
    def next_annotation(self, img):
        self.sam.set_image(img)
        h, w = img.shape[:2]
        self.annotations.append(Annotation(h, w))
        
    def generate_mask(self, points, label):
        if points == []: return
        
        label_arr = np.array(np.full(len(points), label))
        masks, scores, logits = self.sam.predict(point_coords=np.array(points), 
                                                        point_labels=label_arr)
        if self.segment_mode is SegmentMode.SINGLE_POINT:
            self.clear_points()
       
        # process mask output
        if masks == []: return
        mask = masks[0] #(h, w, 1)
        color = np.random.randint(256, size=3, dtype=np.uint8)
        h, w = mask.shape[-2:]
        mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1) #(h, w, 3)
        
        # combine masks
        curr_mask = utils.qt_to_np(self.mask_label.pixmap())
        curr_mask = cv2.cvtColor(curr_mask, cv2.COLOR_RGBA2RGB)
        mask_image = mask_image + curr_mask
        mask_image = mask_image.clip(0, 255).astype("uint8")
        self.mask_label.setPixmap(utils.np_to_qt(mask_image))
        
        
        

        