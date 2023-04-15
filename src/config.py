import os

cwd = os.path.abspath(os.path.dirname(__file__))
os.chdir(cwd)

MODEL_TYPE = 'vit_h'
CHECK_POINT = os.path.join(cwd, 'sam_vit_h_4b8939.pth')

MAX_WIDTH = 640
MAX_HEIGHT = 480

IMG_TYPES = ['*.png', '*.jpg', '*.xpm'] # maybe update later