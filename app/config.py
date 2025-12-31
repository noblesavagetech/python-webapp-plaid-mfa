import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Fix Railway's legacy 'postgres://' prefix for SQLAlchemy
    db_url = os.getenv("DATABASE_URL")
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = db_url or "sqlite:///dev.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-change-in-production")
    
    # Email Settings (Brevo)
    BREVO_API_KEY = os.getenv('BREVO_API_KEY')
    SENDER_EMAIL = os.getenv('SENDER_EMAIL')
    SENDER_NAME = os.getenv('SENDER_NAME', 'BBA Services')
    
    # SMS Settings (Vonage Verify API for 2FA)
    VONAGE_API_KEY = os.getenv('VONAGE_API_KEY')
    VONAGE_API_SECRET = os.getenv('VONAGE_API_SECRET')
    VONAGE_BRAND_NAME = os.getenv('VONAGE_BRAND_NAME', 'BBA Services')
    
    # Security Settings
    SESSION_COOKIE_SECURE = os.getenv('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
