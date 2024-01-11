from pathlib import Path

_dir = Path(__file__).parent

MODEL_TYPE = 'vit_h'
CHECK_POINT = list((_dir / 'assets' / 'models').iterdir())[0]

MAX_WIDTH = 640
MAX_HEIGHT = 480

IMG_TYPES = ['*.png', '*.jpg', '*.xpm'] # maybe update later