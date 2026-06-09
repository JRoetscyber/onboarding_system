import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'onboarding.sqlite'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 60 * 1024 * 1024
    UPLOAD_FOLDER = str(BASE_DIR / "static" / "uploads")

    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "change_me")
    BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")
    COMPANY_NAME = os.getenv("COMPANY_NAME", "JO4 Dev")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@jo4dev.co.za")

    N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "")

    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "hello@jo4dev.co.za")
