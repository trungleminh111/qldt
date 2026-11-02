import os
import shutil
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

if os.environ.get("VERCEL"):
    DATABASE_PATH = "/tmp/qldt.db"
    UPLOAD_FOLDER = "/tmp/uploads"
    source_db = os.path.join(BASE_DIR, "qldt.db")
    if not os.path.exists(DATABASE_PATH) and os.path.exists(source_db):
        try:
            shutil.copy2(source_db, DATABASE_PATH)
        except Exception:
            pass
else:
    DATABASE_PATH = os.path.join(BASE_DIR, "qldt.db")
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

SECRET_KEY = os.environ.get("SECRET_KEY", "qldt_dai_doi_secret_key_2026")
DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1")
PORT = int(os.environ.get("PORT", 5000))
HOST = "0.0.0.0"

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

