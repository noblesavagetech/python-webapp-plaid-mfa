import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Fix Railway's legacy 'postgres://' prefix for SQLAlchemy
    db_url = os.getenv("DATABASE_URL")
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = db_url or "sqlite:///dev.db"  # Fallback for local-first dev
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-keep-it-secret")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-dev-secret-change-in-production")
    
    # Brevo API Settings (HTTP API - Railway blocks SMTP)
    BREVO_API_KEY = os.getenv('BREVO_API_KEY')
    SENDER_EMAIL = os.getenv('SENDER_EMAIL')
    SENDER_NAME = os.getenv('SENDER_NAME', 'BBA Services')
    
    # Application Settings
    APP_URL = os.getenv('APP_URL', 'http://localhost:5000')
    TOKEN_EXPIRATION = int(os.getenv('TOKEN_EXPIRATION', 86400))  # 24 hours default
    
    # Security Settings
    SESSION_COOKIE_SECURE = os.getenv('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
