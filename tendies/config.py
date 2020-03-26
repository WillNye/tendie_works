import os
from pathlib import Path

BASE_DIR = Path(os.path.expanduser('~/.tendie_works'))
os.makedirs(BASE_DIR, exist_ok=True)

TW_TOKEN_DIR = Path(os.path.join(BASE_DIR, 'tw_token.json'))
TW_URL = 'https://api.tastyworks.com'

