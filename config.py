import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "sessions")
LOGO_DIR = os.path.join(BASE_DIR, "data", "logos")
SETTINGS_PATH = os.path.join(BASE_DIR, "data", "settings.json")
DEFAULT_ELETTORI_SEZIONE = 500
SECRET_KEY = os.environ.get("SECRET_KEY", "comunali-proiettore-dev-key")
SOGLIA_VITTORIA = 0.5
TOLLERANZA_VOTI = 2
SCRUTINIO_INCERTO_SOGLIA = 0.70
LOGO_ALLOWED = {"png", "jpg", "jpeg", "webp", "gif", "svg", "bmp"}
LOGO_DISPLAY_SIZE = (320, 320)
LOGO_THUMB_SIZE = (96, 96)
DISPLAY_POLL_MS = 2500
DISPLAY_SEZIONI_PREVIEW = 6
APP_NAME = "Urna Viva"
APP_TAGLINE = "Proiezione comunali in diretta"
