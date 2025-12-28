from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.models import db
from app.utils.sms import send_sms_code, generate_code

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Landing page."""
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard."""
    if not current_user.is_verified:
        return redirect(url_for('auth.verify_email'))
    
    return render_template('dashboard.html')


@main_bp.route('/enable-mfa', methods=['GET', 'POST'])
@login_required
def enable_mfa():
    """Enable SMS-based MFA."""
    if not current_user.is_verified:
        return redirect(url_for('auth.verify_email'))
    
    if current_user.mfa_enabled:
        flash('MFA already enabled.', 'info')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()
        sms_code = request.form.get('sms_code', '').strip()
        
        if not phone and not sms_code:
            # Step 1: Send verification code
            phone = request.form.get('phone', '').strip()
            if not phone:
                flash('Phone number required.', 'danger')
                return render_template('enable_mfa.html')
            
            # Generate and send SMS code
            code = generate_code()
            current_user.sms_code = code
            db.session.commit()
            
            if send_sms_code(phone, code):
                flash('Verification code sent to your phone.', 'success')
                return render_template('enable_mfa.html', phone=phone, step=2)
            else:
                flash('Failed to send SMS.', 'danger')
                return render_template('enable_mfa.html')
        
        elif sms_code:
            # Step 2: Verify code and enable MFA
            phone = request.form.get('phone_hidden')
            
            if current_user.sms_code == sms_code:
                current_user.enable_mfa(phone)
                current_user.sms_code = None  # Clear temp code
                db.session.commit()
                flash('SMS MFA enabled successfully!', 'success')
                return redirect(url_for('main.dashboard'))
            else:
                flash('Invalid verification code.', 'danger')
                return render_template('enable_mfa.html', phone=phone, step=2)
    
    return render_template('enable_mfa.html')


@main_bp.route('/disable-mfa', methods=['POST'])
@login_required
def disable_mfa():
    """Disable MFA."""
    current_user.disable_mfa()
    db.session.commit()
    flash('MFA disabled.', 'info')
    return redirect(url_for('main.dashboard'))