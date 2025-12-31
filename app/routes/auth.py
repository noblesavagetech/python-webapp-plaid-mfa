from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from email_validator import validate_email, EmailNotValidError
from app.models import db, User
from app.utils.email import send_verification_email
from app.utils.sms import send_sms_code, generate_code
import random

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Simple signup with email verification."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        
        # Basic validation
        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('signup.html')
        
        if password != password_confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('signup.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('signup.html')
        
        try:
            validate_email(email)
        except EmailNotValidError:
            flash('Invalid email address.', 'danger')
            return render_template('signup.html')
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('signup.html')
        
        # Create user
        verification_code = str(random.randint(100000, 999999))
        user = User(email=email)
        user.set_password(password)
        user.verification_code = verification_code
        
        db.session.add(user)
        db.session.commit()
        
        # Send verification email
        if send_verification_email(email, verification_code):
            flash('Account created! Check your email for verification code.', 'success')
            login_user(user)
            return redirect(url_for('auth.verify_email'))
        else:
            flash('Account created but email failed to send.', 'warning')
            return redirect(url_for('auth.login'))
    
    return render_template('signup.html')


@auth_bp.route('/verify-email', methods=['GET', 'POST'])
@login_required
def verify_email():
    """Verify email with code."""
    if current_user.is_verified:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        code = request.form.get('verification_code', '').strip()
        
        if current_user.verification_code == code:
            current_user.verify_email()
            db.session.commit()
            flash('Email verified! You can now access your dashboard.', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid verification code.', 'danger')
    
    return render_template('verify_email.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Simple login with optional MFA."""
    if current_user.is_authenticated:
        if not current_user.is_verified:
            return redirect(url_for('auth.verify_email'))
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        sms_code = request.form.get('sms_code', '').strip()
        
        if not email or not password:
            flash('Email and password required.', 'danger')
            return render_template('login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash('Invalid email or password.', 'danger')
            return render_template('login.html')
        
        # Check MFA if enabled (optional)
        if user.mfa_enabled:
            if not sms_code:
                flash('Please enter your SMS code.', 'danger')
                return render_template('login.html', require_mfa=True)
            
            # Import verify function
            from app.utils.sms import verify_sms_code
            
            if not user.vonage_request_id or not verify_sms_code(user.vonage_request_id, sms_code):
                flash('Invalid SMS code.', 'danger')
                return render_template('login.html', require_mfa=True)
            
            # Clear request ID after use
            user.vonage_request_id = None
            db.session.commit()
        
        login_user(user)
        
        if not user.is_verified:
            return redirect(url_for('auth.verify_email'))
        
        return redirect(url_for('main.dashboard'))
    
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout user."""
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/resend-verification')
@login_required
def resend_verification():
    """Resend email verification code."""
    if current_user.is_verified:
        flash('Email already verified.', 'info')
        return redirect(url_for('main.dashboard'))
    
    verification_code = str(random.randint(100000, 999999))
    current_user.verification_code = verification_code
    db.session.commit()
    
    if send_verification_email(current_user.email, verification_code):
        flash('Verification code resent.', 'success')
    else:
        flash('Failed to send email.', 'danger')
    
    return redirect(url_for('auth.verify_email'))


@auth_bp.route('/request-sms-code')
@login_required
def request_sms_code():
    """Send SMS code for MFA login."""
    user = User.query.get(current_user.id)
    
    if not user.mfa_enabled or not user.phone:
        flash('MFA not enabled.', 'danger')
        return redirect(url_for('auth.login'))
    
    # Send SMS code via Vonage - it returns request_id
    request_id = send_sms_code(user.phone, None)  # Vonage generates the code
    if request_id:
        user.vonage_request_id = request_id
        db.session.commit()
        flash(f'SMS code sent to {user.phone[-4:].rjust(len(user.phone), "*")}', 'success')
    else:
        flash('Failed to send SMS.', 'danger')
    
    return redirect(url_for('auth.login'))