from pathlib import Path
import sys

_dir = Path(__file__).parent
_model_path = _dir / 'assets' / 'models'
_model_path.mkdir(parents=True, exist_ok=True)
_checkpoints = list(_model_path.iterdir())

MODEL_TYPE = 'vit_h'
try:
    SAM_CHECK_POINT = _checkpoints[2]
    FAST_SAM_CHECK_POINT = _checkpoints[1]
except:
    print('Failed to find SAM and FastSAM checkpoints! ' \
          f'Please download both and move to {_model_path}')
    sys.exit(1)

CONFIG_PATH = Path('./assets/user_config.json')

MAX_WIDTH = 480
MAX_HEIGHT = 480

IMG_TYPES = ['*.png', '*.jpg', '*.xpm'] # maybe update later