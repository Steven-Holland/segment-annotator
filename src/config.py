from pathlib import Path

_dir = Path(__file__).parent
_model_path = _dir / 'assets' / 'models'
_model_path.mkdir(parents=True, exist_ok=True)
_checkpoints = list(_model_path.iterdir())

MODEL_TYPE = 'vit_h'
SAM_CHECK_POINT = _checkpoints[2]
FAST_SAM_CHECK_POINT = _checkpoints[1]

CONFIG_PATH = Path('./assets/user_config.json')

MAX_WIDTH = 640
MAX_HEIGHT = 640

IMG_TYPES = ['*.png', '*.jpg', '*.xpm'] # maybe update later