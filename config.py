import os
import sys
import shutil
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if getattr(sys, "frozen", False):
    DATA_DIR = os.path.dirname(sys.executable)
    RESOURCE_DIR = getattr(sys, "_MEIPASS", BASE_DIR)
else:
    DATA_DIR = BASE_DIR
    RESOURCE_DIR = BASE_DIR

env_path = os.path.join(DATA_DIR, ".env")
if not os.path.exists(env_path):
    env_path = os.path.join(RESOURCE_DIR, ".env")
if not os.path.exists(env_path):
    env_path = os.path.join(BASE_DIR, ".env")

if os.path.exists(env_path):
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k:
                        os.environ[k] = v
    except Exception:
        pass

DB_BACKEND = os.environ.get("DB_BACKEND", "auto").strip().lower()
DATABASE_URL = os.environ.get("POSTGRES_URL") or os.environ.get("DATABASE_URL")
custom_sqlite = os.environ.get("SQLITE_PATH")

if os.environ.get("VERCEL"):
    DATABASE_PATH = "/tmp/qldt.db"
    UPLOAD_FOLDER = "/tmp/uploads"
    if DB_BACKEND == "sqlite" or (DB_BACKEND == "auto" and not DATABASE_URL):
        source_db = os.path.join(BASE_DIR, "qldt.db")
        if os.path.exists(source_db):
            copy_needed = not os.path.exists(DATABASE_PATH)
            if not copy_needed:
                try:
                    copy_needed = os.path.getmtime(source_db) > os.path.getmtime(DATABASE_PATH)
                except OSError:
                    copy_needed = False
            if copy_needed:
                try:
                    shutil.copy2(source_db, DATABASE_PATH)
                except Exception:
                    pass
elif custom_sqlite:
    if os.path.isabs(custom_sqlite):
        DATABASE_PATH = os.path.abspath(custom_sqlite)
    else:
        DATABASE_PATH = os.path.join(DATA_DIR, custom_sqlite)
    UPLOAD_FOLDER = os.path.join(os.path.dirname(DATABASE_PATH), "uploads")
else:
    DATABASE_PATH = os.path.join(DATA_DIR, "qldt.db")
    UPLOAD_FOLDER = os.path.join(DATA_DIR, "uploads")

SECRET_KEY = os.environ.get("SECRET_KEY", "qldt_dai_doi_secret_key_2026")
DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1")
PORT = int(os.environ.get("PORT", 5000))
HOST = "0.0.0.0"

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
