import numpy as np
import cv2
from PyQt5.QtCore import QObject
from enum import Enum
import utils
from config import MAX_HEIGHT, MAX_WIDTH

class SegmentMode(Enum):
    SINGLE_POINT = 1
    MULTI_POINT = 2
    BOX = 3


class Annotation:
    def __init__(self, input_size, output_size):
        self.height, self.width = input_size
        self.out_height, self.out_width = output_size
        self.clear_mask()

    def append(self, new_mask, label):
        new_mask_labeled = np.where(new_mask, label['value'], new_mask)
        self.out_mask = np.where(new_mask_labeled, new_mask_labeled, self.out_mask)

        color = label['color'].lstrip('#')
        color = np.array(tuple(int(color[i:i+2], 16) for i in (0, 2, 4))) # hex to [r,g,b]

        mask_image = new_mask.reshape(self.height, self.width, 1) * color.reshape(1, 1, -1) #(h, w, 3)
        self.display_mask = np.where(mask_image, mask_image, self.display_mask)
        self.display_mask = self.display_mask.clip(0, 255).astype("uint8")
        
    def get_mask(self):
        return cv2.resize(self.out_mask, (self.out_width, self.out_height))

    def get_mask_image(self):
        return utils.np_to_qt(self.display_mask)
    
    def clear_mask(self):
        print('height:', self.height, 'width:', self.width)
        self.out_mask = np.zeros((self.height, self.width))
        self.display_mask = np.zeros((self.height, self.width, 3))

    


class Labeler(QObject):
    def __init__(self, sam, in_size, out_size):
        super().__init__()
        self.sam = sam

        self.anno_idx = 0
        self.annotations = [Annotation(in_size, out_size)]
        self.segment_mode = SegmentMode.SINGLE_POINT
        
    def next_annotation(self, img_path, in_size, out_size):
        self.sam.set_image(img_path)

        self.anno_idx += 1
        if len(self.annotations) <= self.anno_idx:
            self.annotations.append(Annotation(in_size, out_size))
        
        
    def generate_mask(self, points, label):
        if points == []: 
            print('no points')
            return
        
        label_arr = np.full(len(points), 1)
        masks = self.sam.predict(point_coords=np.array(points), 
                                point_labels=label_arr)
       
        # process mask output
        if masks == []: 
            print('no masks')
            return
        mask = masks[0] #(h, w, 1)
        self.annotations[self.anno_idx].append(mask, label)

    
    def get_mask(self):
        return self.annotations[self.anno_idx].get_mask()
    
    def get_mask_image(self):
        return self.annotations[self.anno_idx].get_mask_image()
    
    def clear_mask(self):
        self.annotations[self.anno_idx].clear_mask()

        
        
        

        