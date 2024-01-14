from pathlib import Path

_dir = Path(__file__).parent
_model_path = _dir / 'assets' / 'models'
_model_path.mkdir(parents=True, exist_ok=True)

MODEL_TYPE = 'vit_h'
CHECK_POINT = list(_model_path.iterdir())[0]

MAX_WIDTH = 640
MAX_HEIGHT = 480

IMG_TYPES = ['*.png', '*.jpg', '*.xpm'] # maybe update later