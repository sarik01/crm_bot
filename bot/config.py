import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

token = os.environ.get('token')

I18N_DOMAIN = 'testbot'
BASE_DIR = Path(__file__).parent
LOCALES_DIR = BASE_DIR / 'locales'