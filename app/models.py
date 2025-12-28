from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Simple user model with email verification and optional SMS MFA."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    
    # Optional MFA fields
    phone = db.Column(db.String(20), nullable=True)
    mfa_enabled = db.Column(db.Boolean, default=False, nullable=False)
    
    # Temporary codes
    verification_code = db.Column(db.String(6), nullable=True)  # Email verification
    sms_code = db.Column(db.String(6), nullable=True)  # SMS MFA code
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    verified_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify the password against the stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def verify_email(self):
        """Mark the user's email as verified."""
        self.is_verified = True
        self.verified_at = datetime.utcnow()
        self.verification_code = None
    
    def enable_mfa(self, phone_number):
        """Enable SMS-based MFA with phone number."""
        self.phone = phone_number
        self.mfa_enabled = True
    
    def disable_mfa(self):
        """Disable MFA."""
        self.mfa_enabled = False
        self.phone = None
        self.sms_code = None


class QuestionnaireResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    answers = db.Column(db.JSON, nullable=False)
    score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class WaveToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    access_token = db.Column(db.String, nullable=False)
    refresh_token = db.Column(db.String)
    expires_at = db.Column(db.DateTime)
