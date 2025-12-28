from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Landing page."""
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Protected dashboard - requires full authentication."""
    if not current_user.is_verified:
        return redirect(url_for('auth.verify_email'))
    
    if not current_user.mfa_enabled:
        return redirect(url_for('auth.setup_mfa'))
    
    return render_template('dashboard.html')