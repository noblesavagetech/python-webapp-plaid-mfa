from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from email_validator import validate_email, EmailNotValidError
from app.models import db, User
from app.utils.email import send_verification_email, send_mfa_setup_email
import random

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user registration with email verification."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        
        # Validation
        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('signup.html')
        
        if password != password_confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('signup.html')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('signup.html')
        
        # Validate email format
        try:
            validate_email(email)
        except EmailNotValidError as e:
            flash(f'Invalid email address: {str(e)}', 'danger')
            return render_template('signup.html')
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with this email already exists.', 'danger')
            return render_template('signup.html')
        
        # Generate 6-digit verification code
        verification_code = str(random.randint(100000, 999999))
        
        # Create new user (is_verified defaults to False)
        new_user = User(email=email)
        new_user.set_password(password)
        new_user.verification_code = verification_code
        
        db.session.add(new_user)
        db.session.commit()
        
        # Send verification email with code
        if send_verification_email(new_user.email, verification_code):
            flash('Account created! Check your email for the verification code.', 'success')
            login_user(new_user)
            return redirect(url_for('auth.verify_email'))
        else:
            flash('Account created, but we could not send the verification email. Please contact support.', 'warning')
            return redirect(url_for('auth.login'))
    
    return render_template('signup.html')


@auth_bp.route('/verify-email', methods=['GET', 'POST'])
@login_required
def verify_email():
    """Verify user's email with the code."""
    if current_user.is_verified:
        return redirect(url_for('auth.setup_mfa'))
    
    if request.method == 'POST':
        code = request.form.get('verification_code', '').strip()
        
        if not code:
            flash('Please enter the verification code.', 'danger')
            return render_template('verify_email.html')
        
        if current_user.verification_code != code:
            flash('Invalid verification code. Please try again.', 'danger')
            return render_template('verify_email.html')
        
        # Mark user as verified
        current_user.verify_email()
        db.session.commit()
        
        flash('Email verified successfully!', 'success')
        return redirect(url_for('auth.setup_mfa'))
    
    return render_template('verify_email.html')


@auth_bp.route('/setup-mfa', methods=['GET', 'POST'])
@login_required
def setup_mfa():
    """Set up TOTP-based MFA."""
    if not current_user.is_verified:
        return redirect(url_for('auth.verify_email'))
    
    if current_user.mfa_enabled:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        totp_token = request.form.get('totp_token', '').strip()
        
        if not totp_token:
            flash('Please enter the TOTP code from your authenticator app.', 'danger')
            return render_template('setup_mfa.html', totp_secret=current_user.totp_secret, totp_uri=current_user.get_totp_uri())
        
        if current_user.verify_totp(totp_token):
            current_user.mfa_enabled = True
            db.session.commit()
            flash('MFA setup complete! You can now access your dashboard.', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid TOTP code. Please try again.', 'danger')
            return render_template('setup_mfa.html', totp_secret=current_user.totp_secret, totp_uri=current_user.get_totp_uri())
    
    # Generate TOTP secret if not exists
    if not current_user.totp_secret:
        current_user.generate_totp_secret()
        db.session.commit()
        
        # Send TOTP setup email
        send_mfa_setup_email(current_user.email, current_user.totp_secret)
    
    return render_template('setup_mfa.html', totp_secret=current_user.totp_secret, totp_uri=current_user.get_totp_uri())


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login with MFA."""
    if current_user.is_authenticated:
        if current_user.is_verified and current_user.mfa_enabled:
            return redirect(url_for('main.dashboard'))
        elif current_user.is_verified:
            return redirect(url_for('auth.setup_mfa'))
        else:
            return redirect(url_for('auth.verify_email'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        totp_token = request.form.get('totp_token', '').strip()
        
        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash('Invalid email or password.', 'danger')
            return render_template('login.html')
        
        # Check if MFA is enabled
        if user.mfa_enabled:
            if not totp_token:
                flash('Please enter your TOTP code.', 'danger')
                return render_template('login.html', require_mfa=True)
            
            if not user.verify_totp(totp_token):
                flash('Invalid TOTP code.', 'danger')
                return render_template('login.html', require_mfa=True)
        
        login_user(user)
        
        # Redirect based on verification/MFA status
        if not user.is_verified:
            return redirect(url_for('auth.verify_email'))
        elif not user.mfa_enabled:
            return redirect(url_for('auth.setup_mfa'))
        else:
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
    
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/resend-verification')
@login_required
def resend_verification():
    """Resend verification code to the current user."""
    if current_user.is_verified:
        flash('Your email is already verified.', 'info')
        return redirect(url_for('auth.setup_mfa'))
    
    # Generate new verification code
    verification_code = str(random.randint(100000, 999999))
    current_user.verification_code = verification_code
    db.session.commit()
    
    if send_verification_email(current_user.email, verification_code):
        flash('Verification code resent! Please check your inbox.', 'success')
    else:
        flash('Failed to send verification code. Please try again later.', 'danger')
    
    return redirect(url_for('auth.verify_email'))