"""
Flask Email Verification App with MFA
Main application package
"""
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from app.models import db, User
from app.routes.auth import auth_bp
from app.routes.main import main_bp
from app.config import Config

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize database
    db.init_app(app)
    Migrate(app, db)  # Handles the 'if exists' schema logic
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    
    return app
