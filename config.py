# config.py
import os
from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).parent.absolute()
APP_DATA_DIR = BASE_DIR / "app_data"

if not APP_DATA_DIR.exists():
    APP_DATA_DIR.mkdir()

DOT_ENV_FILE = BASE_DIR / '.env'
WEBSITES_DATA_JSON = APP_DATA_DIR / 'websites_data.json'
DOT_SESSION_TOKEN_FILE = APP_DATA_DIR / '.session_token'

# Load environment variables from the .env file
load_dotenv(str(DOT_ENV_FILE))

SECRET_KEY = os.environ.get("SECRET_KEY") or "this-is-very-very-strong-secret-key"

BULLET_UNICODE = '\u2022'