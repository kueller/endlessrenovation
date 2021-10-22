import os

API_KEY_SYLVIA = os.environ.get("API_KEY_SYLVIA")
API_KEY_ADMIN = os.environ.get("API_KEY_ADMIN")

APP_SECRET_KEY = os.environ.get("APP_SECRET_KEY")

DATABASE_URI = os.environ.get("DATABASE_URI")

ANTLERS_LYRICS_FILE = os.environ.get("ANTLERS_LYRICS_FILE")

MAIL_SERVER = os.environ.get("MAIL_SERVER")
MAIL_PORT = int(os.environ.get("MAIL_PORT"))
MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
MAIL_ADMIN = os.environ.get("MAIL_ADMIN")
MAIL_HASHFILE = os.environ.get("MAIL_HASHFILE")

HYPH_DB_EN = os.environ.get("HYPH_DB_EN")
HYPH_DB_FR = os.environ.get("HYPH_DB_FR")
HYPH_DB_JP = os.environ.get("HYPH_DB_JP")
HYPH_DB_ES = os.environ.get("HYPH_DB_ES")

SYLLABES_FR_WIKTIONARY_DIR = os.environ.get("SYLLABES_FR_WIKTIONARY_DIR")
