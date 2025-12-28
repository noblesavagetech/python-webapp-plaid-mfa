from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import pyotp

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model with email verification and MFA support."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    
    # MFA fields
    totp_secret = db.Column(db.String(255), nullable=True)
    mfa_enabled = db.Column(db.Boolean, default=False, nullable=False)
    
    # Temporary verification storage
    verification_code = db.Column(db.String(6), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    verified_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_password(self, password):
        """Hash and set the user's password using PBKDF2."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Verify the password against the stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def verify_email(self):
        """Mark the user's email as verified."""
        self.is_verified = True
        self.verified_at = datetime.utcnow()
        self.verification_code = None  # Clear the code
    
    def generate_totp_secret(self):
        """Generate a new TOTP secret for MFA."""
        self.totp_secret = pyotp.random_base32()
    
    def verify_totp(self, token):
        """Verify a TOTP token."""
        if not self.totp_secret or not self.mfa_enabled:
            return False
        totp = pyotp.TOTP(self.totp_secret)
        return totp.verify(token, valid_window=1)
    
    def get_totp_uri(self):
        """Get the TOTP provisioning URI for QR code generation."""
        if not self.totp_secret:
            return None
        return pyotp.totp.TOTP(self.totp_secret).provisioning_uri(
            name=self.email,
            issuer_name='BBA Services'
        )


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
