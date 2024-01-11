import numpy as np
import cv2
from PyQt5.QtCore import QObject
from enum import Enum
from sam_worker import SAM_worker
import utils

class SegmentMode(Enum):
    SINGLE_POINT = 1
    MULTI_POINT = 2
    BOX = 3


class Annotation:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.out_mask = np.zeros((height, width))
        self.display_mask = np.zeros((height, width, 3))

    def append(self, new_mask, label):
        new_mask_labeled = np.where(new_mask, label['value'], new_mask)
        self.out_mask = np.where(new_mask_labeled, new_mask_labeled, self.out_mask)

        color = label['color'].lstrip('#')
        color = np.array(tuple(int(color[i:i+2], 16) for i in (0, 2, 4))) # hex to [r,g,b]

        mask_image = new_mask.reshape(self.height, self.width, 1) * color.reshape(1, 1, -1) #(h, w, 3)
        self.display_mask = self.display_mask + mask_image
        self.display_mask = self.display_mask.clip(0, 255).astype("uint8")
        
    def get_mask(self):
        return self.out_mask

    def get_mask_image(self):
        image = utils.np_to_qt(self.display_mask)
        return image
        
    def __len__(self):
        return len(self.masks)
    


class Labeler(QObject):
    def __init__(self, sam: SAM_worker, height: int, width: int):
        super().__init__()
        self.sam = sam

        self.anno_idx = 0
        self.annotations = [Annotation(height, width)]
        self.segment_mode = SegmentMode.SINGLE_POINT
        
    def next_annotation(self, img):
        self.sam.set_image(img)
        h, w = img.shape[:2]
        self.annotations.append(Annotation(h, w))
        self.anno_idx += 1
        
    def generate_mask(self, points, label):
        if points == []: 
            print('no points')
            return
        
        label_arr = np.array(np.full(len(points), 1))
        masks, scores, logits = self.sam.predict(point_coords=np.array(points), 
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


        # color = np.random.randint(256, size=3, dtype=np.uint8)
        # h, w = mask.shape[-2:]
        # mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1) #(h, w, 3)
        
        # # combine masks
        # curr_mask = utils.qt_to_np(self.mask_label.pixmap())
        # curr_mask = cv2.cvtColor(curr_mask, cv2.COLOR_RGBA2RGB)
        # mask_image = mask_image + curr_mask
        # mask_image = mask_image.clip(0, 255).astype("uint8")
        # self.mask_label.setPixmap(utils.np_to_qt(mask_image))
        
        
        

        