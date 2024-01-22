from pathlib import Path

_dir = Path(__file__).parent
_model_path = _dir / 'assets' / 'models'
_model_path.mkdir(parents=True, exist_ok=True)

MODEL_TYPE = 'vit_h'
CHECK_POINT = list(_model_path.iterdir())[1]

CONFIG_PATH = Path('./assets/user_config.json')

IMG_WIDTH = 320
IMG_HEIGHT = 240

IMG_TYPES = ['*.png', '*.jpg', '*.xpm'] # maybe update later