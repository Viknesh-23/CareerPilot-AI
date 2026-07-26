import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "development-only-change-me")
    database_url = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'careerpilot.db'}")
    SQLALCHEMY_DATABASE_URI = (
        "postgresql://" + database_url[len("postgres://"):]
        if database_url.startswith("postgres://") else database_url
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 8 * 1024 * 1024))
    UPLOAD_FOLDER = str(BASE_DIR / "uploads")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("FLASK_ENV") == "production"
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
