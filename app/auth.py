from flask import Blueprint, request, jsonify, url_for, current_app
from app import db, mail
from app.models import User
from flask_jwt_extended import create_access_token
from flask_mail import Message
from pydantic import BaseModel, EmailStr, ValidationError
import secrets
import pyotp
from itsdangerous import URLSafeTimedSerializer

bp = Blueprint('auth', __name__)


class RegisterModel(BaseModel):
    email: EmailStr
    password: str


@bp.route('/register', methods=['POST'])
def register():
    try:
        data = RegisterModel(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    if User.query.filter_by(email=data.email).first():
        return jsonify({"error": "Email already registered"}), 400
    
    # Generate 6-digit verification code
    import random
    verification_code = str(random.randint(100000, 999999))
    
    user = User(email=data.email, verified=False)
    user.set_password(data.password)
    user.verification_token = verification_code  # Store code temporarily
    user.generate_totp_secret()
    db.session.add(user)
    db.session.commit()

    # Send verification email with code
    html = f'''
    <h2>Welcome to BBA Services!</h2>
    <p>Your verification code is: <strong style="font-size: 24px; color: #667eea;">{verification_code}</strong></p>
    <p>This code will expire in 10 minutes.</p>
    <p>After verification, you'll receive your TOTP setup instructions.</p>
    '''
    msg = Message('Your BBA Services Verification Code', recipients=[user.email], html=html)
    try:
        mail.send(msg)
    except Exception as e:
        return jsonify({"error": f"Failed to send email: {str(e)}"}), 500

    return jsonify({
        "message": "Verification code sent! Check your emails at: http://localhost:8025 or use /api/auth/dev/emails/your-email@example.com",
        "email_viewer": "http://localhost:8025",
        "dev_endpoint": f"/api/auth/dev/emails/{user.email}"
    }), 201


@bp.route('/verify-code', methods=['POST'])
def verify_code():
    json_ = request.json or {}
    email = json_.get('email')
    code = json_.get('code')
    
    if not email or not code:
        return jsonify({"error": "Email and verification code required"}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if user.verified:
        return jsonify({"error": "Email already verified"}), 400
    
    if user.verification_token != code:
        return jsonify({"error": "Invalid verification code"}), 400
    
    # Mark as verified and clear the temporary code
    user.verified = True
    user.verification_token = None  # Clear the code
    db.session.commit()
    
    # Send TOTP setup email
    html = f'''
    <h2>Email Verified Successfully!</h2>
    <p>Your account is now verified. For security, we use two-factor authentication.</p>
    <p><strong>Your TOTP Secret:</strong> {user.totp_secret}</p>
    <p>Set this up in your authenticator app (Google Authenticator, Authy, etc.):</p>
    <ol>
        <li>Open your authenticator app</li>
        <li>Add a new account</li>
        <li>Scan QR code or enter this secret: <code>{user.totp_secret}</code></li>
        <li>Use the generated codes to log in</li>
    </ol>
    <p>You can now log in with your email, password, and TOTP code!</p>
    '''
    msg = Message('BBA Services - TOTP Setup Instructions', recipients=[user.email], html=html)
    try:
        mail.send(msg)
    except Exception as e:
        # Don't fail if TOTP email fails, user is already verified
        pass
    
    return jsonify({
        "message": "Email verified! Check your email for TOTP setup instructions.",
        "totp_secret": user.totp_secret  # Also return in response for convenience
    }), 200


@bp.route('/dev/emails/<email>')
def get_user_emails(email):
    """Development endpoint to view emails for a user (only works with MailHog)"""
    import requests
    try:
        response = requests.get('http://mailhog:8025/api/v2/messages')
        if response.status_code == 200:
            messages = response.json()
            user_emails = []
            for msg in messages['items']:
                to_email = msg['Content']['Headers']['To'][0]
                if email.lower() in to_email.lower():
                    body = msg['Content']['Body']
                    # Extract verification code
                    import re
                    code_match = re.search(r'(\d{6})', body)
                    totp_match = re.search(r'([A-Z0-9]{32})', body)
                    
                    user_emails.append({
                        'subject': msg['Content']['Headers']['Subject'][0],
                        'to': to_email,
                        'verification_code': code_match.group(1) if code_match else None,
                        'totp_secret': totp_match.group(1) if totp_match else None,
                        'timestamp': msg['Created']
                    })
            return jsonify(user_emails)
    except Exception as e:
        return jsonify({"error": f"Could not fetch emails: {str(e)}"}), 500
    
    return jsonify([])


@bp.route('/login', methods=['POST'])
def login():
    json_ = request.json or {}
    email = json_.get('email')
    password = json_.get('password')
    totp_token = json_.get('totp_token')
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401
    if not user.verified:
        return jsonify({"error": "Email not verified"}), 401
    if not user.verify_totp(totp_token):
        return jsonify({"error": "Invalid TOTP token"}), 401
    token = create_access_token(identity=user.id)
    return jsonify({"access_token": token}), 200
